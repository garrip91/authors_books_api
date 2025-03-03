"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/authors_books_app/tests/test_author/author_list_view_test.py::TestAuthorListlView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from authors_books_app.models import Author
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthorListView:
    """Класс тестов для представления AuthorListView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("api_v1:author-list")
        self.user = User.objects.create_user(username="username_for_test", password="password_for_test")

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ СПИСКА ЗАПИСЕЙ ИЗ ТАБЛИЦЫ `Author` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_author_list(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Author.objects.count()

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Author` ПОДКЛЮЧЁННОЙ БД АВТОРИЗОВАННЫМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_create_author_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Мистер",
            "last_name": "Всемогущий",
            "date_of_birth": "1940-01-01",
            "date_of_death": "2020-01-01",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.count() == 1
        assert Author.objects.first().owner == self.user

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСЕЙ В ТАБЛИЦЕ `Author` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_create_author_unauthenticated(self):
        data = {
            "first_name": "Царевна",
            "last_name": "Лягушкина",
            "date_of_birth": "1920-01-01",
            "date_of_death": "2000-01-01",
            "owner": self.user.id,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Author.objects.count() == 0

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Author` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "first_name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_filter_author_by_last_name(self):
        Author.objects.create(first_name="Борис", last_name="Вихров", date_of_birth="1910-01-01")
        Author.objects.create(first_name="Константин", last_name="Ковров", date_of_birth="1930-01-01")
        Author.objects.create(first_name="Михаил", last_name="Поляков", date_of_birth="1950-01-01")
        response = self.client.get(self.url, {"last_name__icontains": "ов"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["last_name"] == "Вихров"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Author` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "last_name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_order_author_by_last_name(self):
        Author.objects.create(first_name="Мистер", last_name="Всемогущий", date_of_birth="1940-01-01")
        Author.objects.create(first_name="Царевна", last_name="Лягушкина", date_of_birth="1920-01-01")
        Author.objects.create(first_name="Господин", last_name="Манушин", date_of_birth="1900-01-01")
        response = self.client.get(self.url, {"ordering": "last_name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["last_name"] == "Всемогущий"
        assert response.data[1]["last_name"] == "Лягушкина"
        assert response.data[2]["last_name"] == "Манушин"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОИСКА ЗАПИСЕЙ В ТАБЛИЦЕ `Author` ПОДКЛЮЧЁННОЙ БД ПО КРИТЕРИЮ "last_name" ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_search_author_by_last_name(self):
        Author.objects.create(first_name="Борис", last_name="Вихров", date_of_birth="1910-01-01")
        Author.objects.create(first_name="Константин", last_name="Ковров", date_of_birth="1930-01-01")
        Author.objects.create(first_name="Михаил", last_name="Поляков", date_of_birth="1950-01-01")
        response = self.client.get(self.url, {"search": "ов"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert response.data[0]["last_name"] == "Вихров"
        assert response.data[1]["last_name"] == "Ковров"
        assert response.data[2]["last_name"] == "Поляков"
