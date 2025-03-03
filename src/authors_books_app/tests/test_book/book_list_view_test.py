"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_book/book_list_view_test.py::TestBookListView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Author, Genre, Book
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestBookListView:
    """Класс тестов для представления BookListView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("api_v1:book-list")
        self.user = User.objects.create_user(username="username_for_test", password="password_for_test")
        self.author = Author.objects.create(
            first_name="Мистер",
            last_name="Всемогущий",
            date_of_birth="1940-01-01",
            date_of_death="2020-01-01",
            owner=self.user  # владелец записи — self.user
        )
        self.genre = Genre.objects.create(
            name="Жанр",
            owner=self.user  # владелец записи — self.user
        )
        self.book = Book.objects.create(
            title="Книга",
            author=self.author,
            short_description="Описание",
            isbn="isbn",
            owner=self.user  # владелец записи — self.user
        )
        self.book.genre.add(self.genre)  # используем метод add() для ManyToManyField, чем связываем книгу с жанром

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ СПИСКА ЗАПИСЕЙ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_book_list(self):
        response = self.client.get(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Book.objects.count()

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Book` ПОДКЛЮЧЁННОЙ БД АВТОРИЗОВАННЫМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_create_book_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Книга",
            "author": self.author.id,
            "short_description": "Описание",
            "genre": [self.genre.id],
            "isbn": "isbn ИЗМ.",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == 2
        assert Book.objects.last().owner == self.user

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСЕЙ В ТАБЛИЦЕ `Book` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_create_book_unauthenticated(self):
        data = {
            "title": "Книга",
            "author": self.author.id,
            "short_description": "Описание",
            "genre": [self.genre.id],
            "isbn": "isbn ИЗМ.",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Book.objects.count() == 1

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Book` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_filter_book_by_name(self):
        Book.objects.create(title="Книга 000123")
        Book.objects.create(title="Книга 000234")
        Book.objects.create(title="Книга 000345")
        response = self.client.get(self.url, {"title__icontains": "3"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4
        assert response.data[1]["title"] == "Книга 000123"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Book` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_order_book_by_name(self):
        Book.objects.create(title="Книга 000123")
        Book.objects.create(title="Книга 000234")
        Book.objects.create(title="Книга 000345")
        response = self.client.get(self.url, {"ordering": "title"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert response.data[1]["title"] == "Книга 000123"
        assert response.data[2]["title"] == "Книга 000234"
        assert response.data[3]["title"] == "Книга 000345"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОИСКА ЗАПИСЕЙ В ТАБЛИЦЕ `Book` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_search_book_by_name(self):
        Book.objects.create(title="Книга 000123")
        Book.objects.create(title="Книга 000234")
        Book.objects.create(title="Книга 000345")
        response = self.client.get(self.url, {"search": "3"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["title"] == "Книга 000123"
        assert response.data[1]["title"] == "Книга 000234"
        assert response.data[2]["title"] == "Книга 000345"
