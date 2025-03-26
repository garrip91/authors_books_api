"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_actor/actor_list_view_test.py::TestActorListView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from kinopoiskapiunofficial_tech_app.models import Actor


User = get_user_model()

@pytest.mark.django_db
class TestActorListView:
    """Класс тестов для представления ActorListView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="username_for_test_1", password="password_for_test_1", is_staff=True)
        self.user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2", is_staff=False)
        self.other_user = User.objects.create_user(username="username_for_test_3", password="password_for_test_3", is_staff=False)
        
        for i in range(1, 6):
            self.actor = Actor.objects.create(
                staff_id=5000+i,
                name=f"Тестовый актёр #{i}",
                poster_url=f"https://example.com/poster_{i}.jpg",
                profession=f"Тестовая профессия #{i} тестового актёра #{i}",
            )

        self.url = reverse("api_v1:actor-list")

################################################################ READ ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ СПИСКА ЗАПИСЕЙ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_actor_list(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Actor.objects.count()
######################################################################################################################################

################################################################ CREATE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД АУТЕНТИФИЦИРОВАННЫМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_create_actor_by_authenticated_user(self):
        self.actor.owner = self.user
        self.actor.save()
        self.client.force_authenticate(user=self.user)
        data = {
            "staff_id": 5006,
            "name": "Тестовый актёр #6",
            "poster_url": "https://example.com/poster_6.jpg",
            "profession": "Тестовая профессия #6 тестового актёра #6",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Actor.objects.count() == 6
        assert Actor.objects.last().staff_id == 5006
        assert Actor.objects.last().name == "Тестовый актёр #6"
        assert Actor.objects.last().poster_url == "https://example.com/poster_6.jpg"
        assert Actor.objects.last().profession == "Тестовая профессия #6 тестового актёра #6"
        assert Actor.objects.last().owner == self.user

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_create_actor_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        data = {
            "staff_id": 5006,
            "name": "Тестовый актёр #6",
            "poster_url": "https://example.com/poster_6.jpg",
            "profession": "Тестовая профессия #6 тестового актёра #6",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Actor.objects.count() == 5
########################################################################################################################################

################################################################ FILTER ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "staff_id":
    def test_filter_actor_by_staff_id_field(self):
        response = self.client.get(self.url, {"staff_id": 5003})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["staff_id"] == 5003
        assert response.data[0]["name"] == "Тестовый актёр #3"
        assert response.data[0]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #3 тестового актёра #3"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "name":
    def test_filter_actor_by_name_field(self):
        response = self.client.get(self.url, {"name": "#3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["staff_id"] == 5003
        assert response.data[0]["name"] == "Тестовый актёр #3"
        assert response.data[0]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #3 тестового актёра #3"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "poster_url":
    def test_filter_actor_by_poster_url_field(self):
        response = self.client.get(self.url, {"poster_url": "_3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["staff_id"] == 5003
        assert response.data[0]["name"] == "Тестовый актёр #3"
        assert response.data[0]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #3 тестового актёра #3"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "profession":
    def test_filter_actor_by_profession_field(self):
        response = self.client.get(self.url, {"profession": "#3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["staff_id"] == 5003
        assert response.data[0]["name"] == "Тестовый актёр #3"
        assert response.data[0]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #3 тестового актёра #3"
########################################################################################################################################

################################################################ ORDERING ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "staff_id":
    def test_ordering_actor_by_staff_id_field(self):
        response = self.client.get(self.url, {"ordering": "-staff_id"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["staff_id"] == 5005
        assert response.data[0]["name"] == "Тестовый актёр #5"
        assert response.data[0]["poster_url"] == "https://example.com/poster_5.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #5 тестового актёра #5"
        assert response.data[1]["staff_id"] == 5004
        assert response.data[1]["name"] == "Тестовый актёр #4"
        assert response.data[1]["poster_url"] == "https://example.com/poster_4.jpg"
        assert response.data[1]["profession"] == "Тестовая профессия #4 тестового актёра #4"
        assert response.data[2]["staff_id"] == 5003
        assert response.data[2]["name"] == "Тестовый актёр #3"
        assert response.data[2]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[2]["profession"] == "Тестовая профессия #3 тестового актёра #3"
        assert response.data[3]["staff_id"] == 5002
        assert response.data[3]["name"] == "Тестовый актёр #2"
        assert response.data[3]["poster_url"] == "https://example.com/poster_2.jpg"
        assert response.data[3]["profession"] == "Тестовая профессия #2 тестового актёра #2"
        assert response.data[4]["staff_id"] == 5001
        assert response.data[4]["name"] == "Тестовый актёр #1"
        assert response.data[4]["poster_url"] == "https://example.com/poster_1.jpg"
        assert response.data[4]["profession"] == "Тестовая профессия #1 тестового актёра #1"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "name":
    def test_ordering_actor_by_name_field(self):
        response = self.client.get(self.url, {"ordering": "-name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["staff_id"] == 5005
        assert response.data[0]["name"] == "Тестовый актёр #5"
        assert response.data[0]["poster_url"] == "https://example.com/poster_5.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #5 тестового актёра #5"
        assert response.data[1]["staff_id"] == 5004
        assert response.data[1]["name"] == "Тестовый актёр #4"
        assert response.data[1]["poster_url"] == "https://example.com/poster_4.jpg"
        assert response.data[1]["profession"] == "Тестовая профессия #4 тестового актёра #4"
        assert response.data[2]["staff_id"] == 5003
        assert response.data[2]["name"] == "Тестовый актёр #3"
        assert response.data[2]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[2]["profession"] == "Тестовая профессия #3 тестового актёра #3"
        assert response.data[3]["staff_id"] == 5002
        assert response.data[3]["name"] == "Тестовый актёр #2"
        assert response.data[3]["poster_url"] == "https://example.com/poster_2.jpg"
        assert response.data[3]["profession"] == "Тестовая профессия #2 тестового актёра #2"
        assert response.data[4]["staff_id"] == 5001
        assert response.data[4]["name"] == "Тестовый актёр #1"
        assert response.data[4]["poster_url"] == "https://example.com/poster_1.jpg"
        assert response.data[4]["profession"] == "Тестовая профессия #1 тестового актёра #1"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "poster_url":
    def test_ordering_actor_by_poster_url_field(self):
        response = self.client.get(self.url, {"ordering": "-poster_url"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["staff_id"] == 5005
        assert response.data[0]["name"] == "Тестовый актёр #5"
        assert response.data[0]["poster_url"] == "https://example.com/poster_5.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #5 тестового актёра #5"
        assert response.data[1]["staff_id"] == 5004
        assert response.data[1]["name"] == "Тестовый актёр #4"
        assert response.data[1]["poster_url"] == "https://example.com/poster_4.jpg"
        assert response.data[1]["profession"] == "Тестовая профессия #4 тестового актёра #4"
        assert response.data[2]["staff_id"] == 5003
        assert response.data[2]["name"] == "Тестовый актёр #3"
        assert response.data[2]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[2]["profession"] == "Тестовая профессия #3 тестового актёра #3"
        assert response.data[3]["staff_id"] == 5002
        assert response.data[3]["name"] == "Тестовый актёр #2"
        assert response.data[3]["poster_url"] == "https://example.com/poster_2.jpg"
        assert response.data[3]["profession"] == "Тестовая профессия #2 тестового актёра #2"
        assert response.data[4]["staff_id"] == 5001
        assert response.data[4]["name"] == "Тестовый актёр #1"
        assert response.data[4]["poster_url"] == "https://example.com/poster_1.jpg"
        assert response.data[4]["profession"] == "Тестовая профессия #1 тестового актёра #1"

    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "profession":
    def test_ordering_actor_by_profession_field(self):
        response = self.client.get(self.url, {"ordering": "-profession"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["staff_id"] == 5005
        assert response.data[0]["name"] == "Тестовый актёр #5"
        assert response.data[0]["poster_url"] == "https://example.com/poster_5.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #5 тестового актёра #5"
        assert response.data[1]["staff_id"] == 5004
        assert response.data[1]["name"] == "Тестовый актёр #4"
        assert response.data[1]["poster_url"] == "https://example.com/poster_4.jpg"
        assert response.data[1]["profession"] == "Тестовая профессия #4 тестового актёра #4"
        assert response.data[2]["staff_id"] == 5003
        assert response.data[2]["name"] == "Тестовый актёр #3"
        assert response.data[2]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[2]["profession"] == "Тестовая профессия #3 тестового актёра #3"
        assert response.data[3]["staff_id"] == 5002
        assert response.data[3]["name"] == "Тестовый актёр #2"
        assert response.data[3]["poster_url"] == "https://example.com/poster_2.jpg"
        assert response.data[3]["profession"] == "Тестовая профессия #2 тестового актёра #2"
        assert response.data[4]["staff_id"] == 5001
        assert response.data[4]["name"] == "Тестовый актёр #1"
        assert response.data[4]["poster_url"] == "https://example.com/poster_1.jpg"
        assert response.data[4]["profession"] == "Тестовая профессия #1 тестового актёра #1"
##########################################################################################################################################

################################################################ SEARCH ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОИСКА ЗАПИСЕЙ В ТАБЛИЦЕ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ (НЕЗАВИСИМО ОТ ПОЛЕЙ):
    def test_search_actor_by_any_field(self):
        response = self.client.get(self.url, {"search": "#3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["staff_id"] == 5003
        assert response.data[0]["name"] == "Тестовый актёр #3"
        assert response.data[0]["poster_url"] == "https://example.com/poster_3.jpg"
        assert response.data[0]["profession"] == "Тестовая профессия #3 тестового актёра #3"
########################################################################################################################################
