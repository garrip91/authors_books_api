"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_film/film_detail_view_test.py::TestFilmDetailView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from kinopoiskapiunofficial_tech_app.models import Film, Actor


User = get_user_model()

@pytest.mark.django_db
class TestFilmDetailView:
    """Класс тестов для представления FilmDetailView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="username_for_test_1", password="password_for_test_1", is_staff=True)
        self.user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2", is_staff=False)
        self.other_user = User.objects.create_user(username="username_for_test_3", password="password_for_test_3", is_staff=False)
        self.film = Film.objects.create(
            kinopoisk_id=1234,
            name="Тестовый фильм #1",
            year=2000,
        )
        self.actor = Actor.objects.create(
            staff_id=67890,
            name="Тестовый актёр",
            poster_url="https://example.com/poster.jpg",
            profession="Тестовая профессия тестового актёра",
        )
        self.film.actors.add(self.actor)
        self.url = reverse("api_v1:film-detail", kwargs={"pk": self.film.pk}) # создаём ссылку для доступа к записи конкретного фильма по ID

################################################################ READ ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_film_detail(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["kinopoisk_id"] == 1234
        assert response.data["name"] == "Тестовый фильм #1"
        assert response.data["year"] == 2000
######################################################################################################################################

################################################################ UPDATE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_update_film_by_owner(self):
        self.film.owner = self.user
        self.film.save()
        self.client.force_authenticate(user=self.user)
        data = {
            "kinopoisk_id": 2468,
            "name": "Тестовый фильм #2",
            "year": 2014,
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.film.refresh_from_db()
        assert self.film.kinopoisk_id == 2468
        assert self.film.name == "Тестовый фильм #2"
        assert self.film.year == 2014

    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД АДМИНОМ ПРОЕКТА:
    def test_update_film_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "kinopoisk_id": 2468,
            "name": "Тестовый фильм #2",
            "year": 2014,
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.film.refresh_from_db()
        assert self.film.kinopoisk_id == 2468
        assert self.film.name == "Тестовый фильм #2"
        assert self.film.year == 2014

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД У ВСЕХ АУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ И АДМИНОВ ПРОЕКТА:
    def test_update_film_by_authenticated_user_who_not_owner_and_not_admin(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "kinopoisk_id": 2468,
            "name": "Тестовый фильм #2",
            "year": 2014,
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.film.refresh_from_db()
        assert self.film.kinopoisk_id == 1234
        assert self.film.name == "Тестовый фильм #1"
        assert self.film.year == 2000

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД У НЕАУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_update_film_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        data = {
            "kinopoisk_id": 2468,
            "name": "Тестовый фильм #2",
            "year": 2014,
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.film.refresh_from_db()
        assert self.film.kinopoisk_id == 1234
        assert self.film.name == "Тестовый фильм #1"
        assert self.film.year == 2000
########################################################################################################################################

################################################################ DELETE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_delete_film_by_owner(self):
        self.film.owner = self.user
        self.film.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Film.objects.filter(pk=self.film.pk).exists()
    
    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД АДМИНАМИ ПРОЕКТА:
    def test_delete_film_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Film.objects.filter(pk=self.film.pk).exists()
    
    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД У ВСЕХ АУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ И АДМИНОВ ПРОЕКТА:
    def test_delete_film_by_authenticated_user_who_not_owner_and_not_admin(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Film.objects.filter(pk=self.film.pk).exists()
    
    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Film` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_delete_film_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Film.objects.filter(pk=self.film.pk).exists()  # запись не удалена'
########################################################################################################################################
