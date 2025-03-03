"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_book/book_detail_view_test.py::TestBookDetailView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Author, Genre, Book
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestBookDetailView:
    """Класс тестов для представления BookDetailView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="username_for_test_1", password="password_for_test_1")
        self.other_user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2")
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
        self.url = reverse("api_v1:book-detail", kwargs={"pk": self.book.pk}) # создаём ссылку для доступа к записи конкретной книги по ID

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_book_detail(self):
        response = self.client.get(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Книга"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_update_book_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Книга ИЗМ.", # пытаемся изменить название книги
            "author": self.author.id,
            "short_description": "Описание",
            "genre": [self.genre.id],
            "isbn": "isbn",
            "owner": self.user.id
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        self.book.refresh_from_db()
        assert self.book.title == "Книга ИЗМ." # название книги изменилось

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_update_book_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "title": "Книга ИЗМ.", # пытаемся изменить название книги
            "author": self.author.id,
            "short_description": "Описание",
            "genre": [self.genre.id],
            "isbn": "isbn",
            "owner": self.other_user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.book.refresh_from_db()
        assert self.book.title == "Книга" # название книги не изменилось

    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_delete_book_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(pk=self.book.pk).exists()

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_delete_book_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Book.objects.filter(pk=self.book.pk).exists() # запись не удалена

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_update_book_unauthenticated(self):
        data = {
            "title": "Книга ИЗМ.", # пытаемся изменить название книги
            "author": self.author.id,
            "short_description": "Описание",
            "genre": [self.genre.id],
            "isbn": "isbn",
            "owner": self.user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.book.refresh_from_db()
        assert self.book.title == "Книга" # название книги не изменилось

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Book` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_delete_book_unauthenticated(self):
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Book.objects.filter(pk=self.book.pk).exists()  # запись не удалена
