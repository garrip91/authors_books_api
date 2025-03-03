"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_genre/genre_list_view_test.py::TestGenreListView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Genre
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestGenreListView:
    """Класс тестов для представления GenreListView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("api_v1:genre-list")
        self.user = User.objects.create_user(username="username_for_test", password="password_for_test")

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ СПИСКА ЗАПИСЕЙ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_genre_list(self):
        response = self.client.get(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Genre.objects.count()

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Genre` ПОДКЛЮЧЁННОЙ БД АВТОРИЗОВАННЫМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_create_genre_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Жанр",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_201_CREATED
        assert Genre.objects.count() == 1
        assert Genre.objects.first().owner == self.user

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСЕЙ В ТАБЛИЦЕ `Genre` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_create_genre_unauthenticated(self):
        data = {
            "name": "Жанр",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Genre.objects.count() == 0

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Genre` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_filter_genre_by_name(self):
        Genre.objects.create(name="Жанр 000123")
        Genre.objects.create(name="Жанр 000234")
        Genre.objects.create(name="Жанр 000345")
        response = self.client.get(self.url, {"name__icontains": "3"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["name"] == "Жанр 000123"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Genre` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_order_genre_by_name(self):
        Genre.objects.create(name="Жанр 000123")
        Genre.objects.create(name="Жанр 000234")
        Genre.objects.create(name="Жанр 000345")
        response = self.client.get(self.url, {"ordering": "name"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["name"] == "Жанр 000123"
        assert response.data[1]["name"] == "Жанр 000234"
        assert response.data[2]["name"] == "Жанр 000345"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОИСКА ЗАПИСЕЙ В ТАБЛИЦЕ `Genre` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_search_genre_by_name(self):
        Genre.objects.create(name="Жанр 000123")
        Genre.objects.create(name="Жанр 000234")
        Genre.objects.create(name="Жанр 000345")
        response = self.client.get(self.url, {"search": "3"})
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["name"] == "Жанр 000123"
        assert response.data[1]["name"] == "Жанр 000234"
        assert response.data[2]["name"] == "Жанр 000345"
