"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_actor/actor_detail_view_test.py::TestActorDetailView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from kinopoiskapiunofficial_tech_app.models import Actor


User = get_user_model()

@pytest.mark.django_db
class TestActorDetailView:
    """Класс тестов для представления ActorDetailView"""

    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="username_for_test_1", password="password_for_test_1", is_staff=True)
        self.user = User.objects.create_user(username="username_for_test_2", password="password_for_test_2", is_staff=False)
        self.other_user = User.objects.create_user(username="username_for_test_3", password="password_for_test_3", is_staff=False)
        self.actor = Actor.objects.create(
            staff_id=67890,
            name="Тестовый актёр #1",
            poster_url="https://example.com/poster_#1.jpg",
            profession="Тестовая профессия #1 тестового актёра #1",
        )
        self.url = reverse("api_v1:actor-detail", kwargs={"pk": self.actor.pk}) # создаём ссылку для доступа к записи конкретного актёра по ID

################################################################ READ ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ПОЛУЧЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД ВСЕМИ ПОЛЬЗОВАТЕЛЯМИ:
    def test_get_actor_detail(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["staff_id"] == 67890
        assert response.data["name"] == "Тестовый актёр #1"
        assert response.data["poster_url"] == "https://example.com/poster_#1.jpg"
        assert response.data["profession"] == "Тестовая профессия #1 тестового актёра #1"
######################################################################################################################################

################################################################ UPDATE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_update_actor_by_owner(self):
        self.actor.owner = self.user
        self.actor.save()
        self.client.force_authenticate(user=self.user)
        data = {
            "staff_id": 56789,
            "name": "Тестовый актёр #2",
            "poster_url": "https://example.com/poster_#2.jpg",
            "profession": "Тестовая профессия #2 тестового актёра #2",
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.actor.refresh_from_db()
        assert self.actor.staff_id == 56789
        assert self.actor.name == "Тестовый актёр #2"
        assert self.actor.poster_url == "https://example.com/poster_#2.jpg"
        assert self.actor.profession == "Тестовая профессия #2 тестового актёра #2"

    # ПРОВЕРКА ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД АДМИНОМ ПРОЕКТА:
    def test_update_actor_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "staff_id": 56789,
            "name": "Тестовый актёр #2",
            "poster_url": "https://example.com/poster_#2.jpg",
            "profession": "Тестовая профессия #2 тестового актёра #2",
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.actor.refresh_from_db()
        assert self.actor.staff_id == 56789
        assert self.actor.name == "Тестовый актёр #2"
        assert self.actor.poster_url == "https://example.com/poster_#2.jpg"
        assert self.actor.profession == "Тестовая профессия #2 тестового актёра #2"

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД У ВСЕХ АУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ И АДМИНОВ ПРОЕКТА:
    def test_update_actor_by_authenticated_user_who_not_owner_and_not_admin(self):
        self.client.force_authenticate(user=self.other_user)
        data = {
            "staff_id": 56789,
            "name": "Тестовый актёр #2",
            "poster_url": "https://example.com/poster_#2.jpg",
            "profession": "Тестовая профессия #2 тестового актёра #2",
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.actor.refresh_from_db()
        assert self.actor.staff_id == 67890
        assert self.actor.name == "Тестовый актёр #1"
        assert self.actor.poster_url == "https://example.com/poster_#1.jpg"
        assert self.actor.profession == "Тестовая профессия #1 тестового актёра #1"

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ ОБНОВЛЕНИЯ ДЕТАЛЕЙ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД У НЕАУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_update_actor_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        data = {
            "staff_id": 56789,
            "name": "Тестовый актёр #2",
            "poster_url": "https://example.com/poster_#2.jpg",
            "profession": "Тестовая профессия #2 тестового актёра #2",
        }
        response = self.client.put(self.url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.actor.refresh_from_db()
        assert self.actor.staff_id == 67890
        assert self.actor.name == "Тестовый актёр #1"
        assert self.actor.poster_url == "https://example.com/poster_#1.jpg"
        assert self.actor.profession == "Тестовая профессия #1 тестового актёра #1"
########################################################################################################################################

################################################################ DELETE ################################################################
    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД ВЛАДЕЛЬЦЕМ ЗАПИСИ:
    def test_delete_actor_by_owner(self):
        self.actor.owner = self.user
        self.actor.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Actor.objects.filter(pk=self.actor.pk).exists()

    # ПРОВЕРКА ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД АДМИНАМИ ПРОЕКТА:
    def test_delete_actor_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Actor.objects.filter(pk=self.actor.pk).exists()

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД У ВСЕХ АУТЕНТИФИЦИРОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ, КРОМЕ ВЛАДЕЛЬЦА ЗАПИСИ И АДМИНОВ ПРОЕКТА:
    def test_delete_actor_by_authenticated_user_who_not_owner_and_not_admin(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Actor.objects.filter(pk=self.actor.pk).exists()

    # ПРОВЕРКА ОТСУТСТВИЯ ВОЗМОЖНОСТИ УДАЛЕНИЯ КОНКРЕТНОЙ ЗАПИСИ ИЗ ТАБЛИЦЫ `Actor` ПОДКЛЮЧЁННОЙ БД У НЕАВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ:
    def test_delete_actor_by_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Actor.objects.filter(pk=self.actor.pk).exists()
########################################################################################################################################
