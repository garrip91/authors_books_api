"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_api_sync/download_films_and_actors_by_get_method_view_test.py::TestDownloadFilmsAndActorsByGETMethodView -v && coverage report
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from kinopoiskapiunofficial_tech_app.models import Film, Actor
from kinopoiskapiunofficial_tech_app.api_sync import APISynchronizer


User = get_user_model()

@pytest.mark.django_db
class TestDownloadFilmsAndActorsByGETMethodView:
    """Класс тестов для представления DownloadFilmsAndActorsByGETMethodView"""
    
    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_for_test", 
            password="password_for_test", 
            is_staff=True
        )
        self.user = User.objects.create_user(
            username="user_for_test", 
            password="password_for_test", 
            is_staff=False
        )
        self.url = reverse("api_v1:download-films-and-actors-by-get-method")
    
    ################################################################ УСПЕШНАЯ СИНХРОНИЗАЦИЯ ################################################################
    def test_successful_sync_by_admin(self, mocker):
        """Проверка успешной синхронизации администратором"""
        # Мокируем APISynchronizer
        mock_sync = mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            return_value={
                "synced_count": 5,
                "total_pages": 10,
                "current_page": 1
            }
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "message": "Информация о 5 фильмах и их актёрах успешно загружена в Вашу базу данных!",
            "page": 1,
            "total_pages": 10
        }
        mock_sync.assert_called_once_with(page=1, user=self.admin)

    def test_successful_sync_by_owner_with_custom_page(self, mocker):
        """Проверка успешной синхронизации владельцем с указанием страницы"""
        # Мокируем APISynchronizer
        mock_sync = mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            return_value={
                "synced_count": 3,
                "total_pages": 5,
                "current_page": 2
            }
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.url}?page=2")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "message": "Информация о 3 фильмах и их актёрах успешно загружена в Вашу базу данных!",
            "page": 2,
            "total_pages": 5
        }
        mock_sync.assert_called_once_with(page=2, user=self.user)

    ################################################################ ОШИБКИ СИНХРОНИЗАЦИИ ################################################################
    def test_sync_error_by_admin(self, mocker):
        """Проверка обработки ошибки при синхронизации"""
        # Мокируем APISynchronizer для вызова исключения
        mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            side_effect=Exception("Тестовое сообщение об ошибке!")
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"error": "Тестовое сообщение об ошибке!"}

    ################################################################ ПРОВЕРКИ ДОСТУПА ################################################################
    def test_access_denied_for_unauthenticated_user(self):
        """Проверка запрета доступа для неаутентифицированных пользователей"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_access_allowed_for_regular_user(self, mocker):
        """Проверка доступа для обычного пользователя (не админа)"""
        # Мокируем успешный вызов, так как проверяем только доступ
        mock_sync = mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            return_value={
                "synced_count": 1,
                "total_pages": 1,
                "current_page": 1
            }
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        mock_sync.assert_called_once()

    ################################################################ ПАРАМЕТРЫ ЗАПРОСА ################################################################
    def test_default_page_parameter(self, mocker):
        """Проверка использования страницы по умолчанию, если она не указана явно"""
        mock_sync = mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            return_value={
                "synced_count": 1,
                "total_pages": 1,
                "current_page": 1
            }
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        mock_sync.assert_called_once_with(page=1, user=self.admin)

    def test_custom_page_parameter(self, mocker):
        """Проверка передачи указанной страницы"""
        mock_sync = mocker.patch.object(
            APISynchronizer,
            "sync_films_and_actors",
            return_value={
                "synced_count": 1,
                "total_pages": 10,
                "current_page": 5
            }
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"{self.url}?page=5")
        
        assert response.status_code == status.HTTP_200_OK
        mock_sync.assert_called_once_with(page=5, user=self.admin)

    def test_invalid_page_parameter(self, mocker):
        """Проверка обработки неверного параметра страницы"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"{self.url}?page=invalid")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
