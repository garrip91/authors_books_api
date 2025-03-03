"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_author/author_detail_view_test.py::TestAuthorDetailView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Author
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthorDetailView:
    """Класс тестов для представления AuthorDetailView"""

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
        self.url = reverse("api_v1:author-detail", kwargs={"pk": self.author.pk}) # создаём ссылку для доступа к записи конкретного автора по ID

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_author_detail(self):
        response = self.client.get(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Мистер"
        assert response.data["last_name"] == "Всемогущий"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_update_author_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Мистер",
            "last_name": "Могущественный", # пытаемся изменить фамилию
            "date_of_birth": "1940-01-01",
            "date_of_death": "2020-01-01",
            "owner": self.user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_200_OK
        self.author.refresh_from_db()
        assert self.author.last_name == "Могущественный" # фамилия изменилась

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_update_author_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "first_name": "Мистер",
            "last_name": "Могущественный", # пытаемся изменить фамилию
            "date_of_birth": "1940-01-01",
            "date_of_death": "2020-01-01",
            "owner": self.other_user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.author.refresh_from_db()
        assert self.author.last_name == "Всемогущий" # фамилия не изменилась

    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_delete_author_authenticated_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Author.objects.filter(pk=self.author.pk).exists()

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД У ВСЕХ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ:
    def test_delete_author_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Author.objects.filter(pk=self.author.pk).exists() # запись не удалена

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_update_author_unauthenticated(self):
        data = {
            "first_name": "Мистер",
            "last_name": "Могущественный", # пытаемся изменить фамилию
            "date_of_birth": "1940-01-01",
            "date_of_death": "2020-01-01",
            "owner": self.user.id,
        }
        response = self.client.put(self.url, data, format="json")
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.author.refresh_from_db()
        assert self.author.last_name == "Всемогущий"  # фамилия не изменилась

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_delete_author_unauthenticated(self):
        response = self.client.delete(self.url)
        print(f"****[[ {response.data} ]]****")  # вывод содержимого ответа сервера для отладки
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Author.objects.filter(pk=self.author.pk).exists()  # запись не удалена
