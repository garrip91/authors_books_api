"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_film/film_list_view_test.py::TestFilmListView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from kinopoiskapiunofficial_tech_app.models import Film, Actor


User = get_user_model()

@pytest.mark.django_db
class TestFilmListView:
    """Класс тестов для представления FilmListView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="username_for_test_1", password="password_for_test_1", is_staff=True)
        self.user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2", is_staff=False)
        self.other_user = User.objects.create_user(username="username_for_test_3", password="password_for_test_3", is_staff=False)
        
        for i in range(1, 6):
            self.film = Film.objects.create(
                kinopoisk_id=1000+i,
                name=f"Тестовый фильм #{i}",
                year=2000+i,
            )
            self.actor = Actor.objects.create(
                staff_id=5000+i,
                name=f"Тестовый актёр #{i}",
                poster_url=f"https://example.com/poster_{i}.jpg",
                profession="Тестовая профессия #{i} тестового актёра #{i}",
            )
            self.film.actors.add(self.actor)

        self.url = reverse("api_v1:film-list")

################################################################ READ ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ СПИСКА ЗАПИСЕЙ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_film_list(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Film.objects.count()
######################################################################################################################################

################################################################ CREATE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД АУТЕНТИФИЦИРОВАННЫМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_create_film_by_authenticated_user(self):
        self.film.owner = self.user
        self.film.save()
        self.client.force_authenticate(user=self.user)
        data = {
            "kinopoisk_id": 1500,
            "name": "Тестовый фильм #5",
            "year": 2005,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Film.objects.count() == 6
        assert Film.objects.last().kinopoisk_id == 1500
        assert Film.objects.last().name == "Тестовый фильм #5"
        assert Film.objects.last().year == 2005
        assert Film.objects.last().owner == self.user
    
    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ СОЗДАНИЯ ЗАПИСИ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_create_film_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        data = {
            "kinopoisk_id": 1500,
            "name": "Тестовый фильм #5",
            "year": 2005,
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Film.objects.count() == 5
########################################################################################################################################

################################################################ FILTER ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "kinopoisk_id":
    def test_filter_film_by_kinopoisk_id_field(self):
        response = self.client.get(self.url, {"kinopoisk_id": 1005})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["kinopoisk_id"] == 1005
        assert response.data[0]["name"] == "Тестовый фильм #5"
        assert response.data[0]["year"] == 2005
    
    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "name":
    def test_filter_film_by_name_field(self):
        response = self.client.get(self.url, {"name__icontains": "фильм"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5
        assert response.data[0]["kinopoisk_id"] == 1001
        assert response.data[0]["name"] == "Тестовый фильм #1"
        assert response.data[0]["year"] == 2001
        assert response.data[1]["kinopoisk_id"] == 1002
        assert response.data[1]["name"] == "Тестовый фильм #2"
        assert response.data[1]["year"] == 2002
        assert response.data[2]["kinopoisk_id"] == 1003
        assert response.data[2]["name"] == "Тестовый фильм #3"
        assert response.data[2]["year"] == 2003
        assert response.data[3]["kinopoisk_id"] == 1004
        assert response.data[3]["name"] == "Тестовый фильм #4"
        assert response.data[3]["year"] == 2004
        assert response.data[4]["kinopoisk_id"] == 1005
        assert response.data[4]["name"] == "Тестовый фильм #5"
        assert response.data[4]["year"] == 2005
    
    # ПРОВЕРКА ВОЗМОЖНОСТИ ФИЛЬТРАЦИИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "year":
    def test_filter_film_by_year_field(self):
        response = self.client.get(self.url, {"year_gte": 2001, "year_lte": 2005})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5
        assert response.data[0]["kinopoisk_id"] == 1001
        assert response.data[0]["name"] == "Тестовый фильм #1"
        assert response.data[0]["year"] == 2001
        assert response.data[1]["kinopoisk_id"] == 1002
        assert response.data[1]["name"] == "Тестовый фильм #2"
        assert response.data[1]["year"] == 2002
        assert response.data[2]["kinopoisk_id"] == 1003
        assert response.data[2]["name"] == "Тестовый фильм #3"
        assert response.data[2]["year"] == 2003
        assert response.data[3]["kinopoisk_id"] == 1004
        assert response.data[3]["name"] == "Тестовый фильм #4"
        assert response.data[3]["year"] == 2004
        assert response.data[4]["kinopoisk_id"] == 1005
        assert response.data[4]["name"] == "Тестовый фильм #5"
        assert response.data[4]["year"] == 2005
########################################################################################################################################

################################################################ ORDERING ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "kinopoisk_id":
    def test_ordering_film_by_kinopoisk_id_field(self):
        response = self.client.get(self.url, {"ordering": "-kinopoisk_id"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["kinopoisk_id"] == 1005
        assert response.data[0]["name"] == "Тестовый фильм #5"
        assert response.data[0]["year"] == 2005
        assert response.data[1]["kinopoisk_id"] == 1004
        assert response.data[1]["name"] == "Тестовый фильм #4"
        assert response.data[1]["year"] == 2004
        assert response.data[2]["kinopoisk_id"] == 1003
        assert response.data[2]["name"] == "Тестовый фильм #3"
        assert response.data[2]["year"] == 2003
        assert response.data[3]["kinopoisk_id"] == 1002
        assert response.data[3]["name"] == "Тестовый фильм #2"
        assert response.data[3]["year"] == 2002
        assert response.data[4]["kinopoisk_id"] == 1001
        assert response.data[4]["name"] == "Тестовый фильм #1"
        assert response.data[4]["year"] == 2001
    
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "name":
    def test_ordering_film_by_name_field(self):
        response = self.client.get(self.url, {"ordering": "-name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["kinopoisk_id"] == 1005
        assert response.data[0]["name"] == "Тестовый фильм #5"
        assert response.data[0]["year"] == 2005
        assert response.data[1]["kinopoisk_id"] == 1004
        assert response.data[1]["name"] == "Тестовый фильм #4"
        assert response.data[1]["year"] == 2004
        assert response.data[2]["kinopoisk_id"] == 1003
        assert response.data[2]["name"] == "Тестовый фильм #3"
        assert response.data[2]["year"] == 2003
        assert response.data[3]["kinopoisk_id"] == 1002
        assert response.data[3]["name"] == "Тестовый фильм #2"
        assert response.data[3]["year"] == 2002
        assert response.data[4]["kinopoisk_id"] == 1001
        assert response.data[4]["name"] == "Тестовый фильм #1"
        assert response.data[4]["year"] == 2001
    
    # ПРОВЕРКА ВОЗМОЖНОСТИ СОРТИРОВКИ ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ ПО ПОЛЮ "year":
    def test_ordering_film_by_year_field(self):
        response = self.client.get(self.url, {"ordering": "-year"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["kinopoisk_id"] == 1005
        assert response.data[0]["name"] == "Тестовый фильм #5"
        assert response.data[0]["year"] == 2005
        assert response.data[1]["kinopoisk_id"] == 1004
        assert response.data[1]["name"] == "Тестовый фильм #4"
        assert response.data[1]["year"] == 2004
        assert response.data[2]["kinopoisk_id"] == 1003
        assert response.data[2]["name"] == "Тестовый фильм #3"
        assert response.data[2]["year"] == 2003
        assert response.data[3]["kinopoisk_id"] == 1002
        assert response.data[3]["name"] == "Тестовый фильм #2"
        assert response.data[3]["year"] == 2002
        assert response.data[4]["kinopoisk_id"] == 1001
        assert response.data[4]["name"] == "Тестовый фильм #1"
        assert response.data[4]["year"] == 2001
##########################################################################################################################################

################################################################ SEARCH ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОИСКА ЗАПИСЕЙ В ТАБЛИЦЕ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ (НЕЗАВИСИМО ОТ ПОЛЕЙ):
    def test_search_film_by_any_field(self):
        response = self.client.get(self.url, {"search": "#3"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["kinopoisk_id"] == 1003
        assert response.data[0]["name"] == "Тестовый фильм #3"
        assert response.data[0]["year"] == 2003
########################################################################################################################################
