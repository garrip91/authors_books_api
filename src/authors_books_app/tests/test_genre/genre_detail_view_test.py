"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_genre/genre_detail_view_test.py::TestGenreDetailView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Genre
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestGenreDetailView:
    """Класс тестов для представления GenreDetailView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="username_for_test_1", password="password_for_test_1")
        self.other_user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2")
        self.genre = Genre.objects.create(
            name="Жанр",
            owner=self.user  # владелец записи — self.user
        )
        self.url = reverse("api_v1:genre-detail", kwargs={"pk": self.genre.pk}) # создаём ссылку для доступа к записи конкретного жанра по ID

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_genre_detail(self):
        response = self.client.get(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Жанр"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_update_genre_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Жанр изменённый", # пытаемся изменить название жанра
            "owner": self.user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        self.genre.refresh_from_db()
        assert self.genre.name == "Жанр изменённый" # название жанра изменилось

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_update_genre_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "name": "Жанр изменённый", # пытаемся изменить название жанра
            "owner": self.other_user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.genre.refresh_from_db()
        assert self.genre.name == "Жанр" # название жанра не изменилось

    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_delete_genre_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Genre.objects.filter(pk=self.genre.pk).exists()

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_delete_genre_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Genre.objects.filter(pk=self.genre.pk).exists() # запись не удалена

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_update_genre_unauthenticated(self):
        data = {
            "name": "Жанр изменённый", # пытаемся изменить название жанра
            "owner": self.user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.genre.refresh_from_db()
        assert self.genre.name == "Жанр" # название жанра не изменилось

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Genre` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_delete_genre_unauthenticated(self):
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Genre.objects.filter(pk=self.genre.pk).exists()  # запись не удалена
