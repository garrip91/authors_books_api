"""
~/programming/django_projects/authors_books_api$ coverage run -m pytest src/kinopoiskapiunofficial_tech_app/tests/test_api_sync/api_sync_test.py::TestAPISynchronizer -v && coverage report
"""

import pytest
from django.contrib.auth import get_user_model
import requests
from kinopoiskapiunofficial_tech_app.models import Film, Actor
from kinopoiskapiunofficial_tech_app.api_sync import APISynchronizer


User = get_user_model()

@pytest.mark.django_db
class TestAPISynchronizer:
    """Класс тестов для APISynchronizer"""
    
    # МЕТОД КЛАССА (ФИКСТУРА) С ДЕКОРАТОРОМ ДЛЯ ИНИЦИАЛИЗАЦИИ ВХОДНЫХ ДАННЫХ ПЕРЕД КАЖДЫМ ТЕСТОМ:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = User.objects.create_user(username="username_for_test", password="password_for_test", is_staff=False)
        self.synchronizer = APISynchronizer()
    
    ################################################################ ТЕСТИРУЕМ СИНХРОНИЗАЦИЮ ИНФОРМАЦИИ О ФИЛЬМАХ И АКТЁРАХ С НАШЕЙ БД ################################################################
    def test_sync_films_and_actors_success(self, mocker):
        # МОКАЕМ ОТВЕТ API ДЛЯ ФИЛЬМА:
        mock_get_films = mocker.patch(
            "kinopoiskapiunofficial_tech_app.api_sync.APISynchronizer.get_films",
            return_value={
                "items": [
                    {
                        "kinopoiskId": 123,
                        "nameRu": "Тестовый фильм",
                        "year": 2014,
                    },
                ],
                "totalPages": 1
            }
        )
        
        # МОКАЕМ ОТВЕТ API ДЛЯ АКТЁРОВ (НЕСКОЛЬКО АКТЁРОВ ДЛЯ ОДНОГО ФИЛЬМА):
        mock_get_actors = mocker.patch(
            "kinopoiskapiunofficial_tech_app.api_sync.APISynchronizer.get_actors",
            return_value=[
                {
                    "staffId": 456,
                    "nameRu": "Тестовый актёр #1",
                    "posterUrl": "https://example.com/poster_1.jpg",
                    "professionText": "Актёр"
                },
                {
                    "staffId": 789,
                    "nameRu": "Тестовый актёр #2",
                    "posterUrl": "https://example.com/poster_2.jpg",
                    "professionText": "Актёр"
                },
                {
                    "staffId": 101,
                    "nameRu": "Тестовый режиссёр",
                    "posterUrl": "https://example.com/poster_3.jpg",
                    "professionText": "Режиссёр"
                },
            ]
        )
        
        # ВЫЗЫВАЕМ МЕТОД ДЛЯ СИНХРОНИЗАЦИИ:
        result = self.synchronizer.sync_films_and_actors(page=1, user=self.user)
        
        # ПРОВЕРЯЕМ РЕЗУЛЬТАТЫ:
        assert result == {
            "synced_count": 1,
            "total_pages": 1,
            "current_page": 1
        }
        
        # ПРОВЕРЯЕМ СОЗДАНИЕ ФИЛЬМА:
        assert Film.objects.count() == 1
        film = Film.objects.first()
        assert film.kinopoisk_id == 123
        assert film.name == "Тестовый фильм"
        assert film.year == 2014
        
        # ПРОВЕРЯЕМ СОЗДАНИЕ ВСЕХ АКТЁРОВ:
        assert Actor.objects.count() == 3

        # ПРОВЕРЯЕМ ДАННЫЕ АКТЁРОВ:
        actors = film.actors.all()
        assert len(actors) == 3

        actor_1 = actors.get(staff_id=456)
        assert actor_1.name == "Тестовый актёр #1"
        assert actor_1.poster_url == "https://example.com/poster_1.jpg"
        assert actor_1.profession == "Актёр"

        actor_2 = actors.get(staff_id=789)
        assert actor_2.name == "Тестовый актёр #2"
        assert actor_2.poster_url == "https://example.com/poster_2.jpg"
        assert actor_2.profession == "Актёр"

        actor_3 = actors.get(staff_id=101)
        assert actor_3.name == "Тестовый режиссёр"
        assert actor_3.poster_url == "https://example.com/poster_3.jpg"
        assert actor_3.profession == "Режиссёр"
        
        # ПРОВЕРЯЕМ ВЫЗОВЫ API:
        mock_get_films.assert_called_once_with(1)
        mock_get_actors.assert_called_once_with(film_id=123)
    
    def test_sync_films_and_actors_with_film_api_error(self, mocker):
        mocker.patch(
            "kinopoiskapiunofficial_tech_app.api_sync.APISynchronizer.get_films",
            side_effect=Exception("API error")
        )
        
        with pytest.raises(Exception, match="API error"):
            self.synchronizer.sync_films_and_actors()
    
    def test_sync_films_and_actors_with_actor_api_error(self, mocker):
        mocker.patch(
            "kinopoiskapiunofficial_tech_app.api_sync.APISynchronizer.get_films",
            return_value={
                "items": [{"kinopoiskId": 123, "nameRu": "Фильм", "year": 2023}],
                "totalPages": 1
            }
        )
        
        mocker.patch(
            "kinopoiskapiunofficial_tech_app.api_sync.APISynchronizer.get_actors",
            side_effect=Exception("Actors API error")
        )
        
        result = self.synchronizer.sync_films_and_actors()
        assert result["synced_count"] == 1
        assert Film.objects.count() == 1
        assert Film.objects.first().actors.count() == 0
    ###############################################################################################################################################################################
    
    ################################################################ ТЕСТИРУЕМ ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ФИЛЬМАХ ################################################################
    def test_get_films_success(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"films": "data"}
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        result = self.synchronizer.get_films()
        assert result == {"films": "data"}
    
    def test_get_films_error(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        with pytest.raises(Exception, match="Ошибка при запросе к API: 404"):
            self.synchronizer.get_films()
    ###############################################################################################################################################################
    
    ################################################################ ТЕСТИРУЕМ ПОЛУЧЕНИЕ ИНФОРМАЦИИ ОБ АКТЁРАХ ################################################################
    def test_get_actors_success(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"actor": "data"}]
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        result = self.synchronizer.get_actors(film_id=123)
        assert result == [{"actor": "data"}]
    
    def test_get_actors_error(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        with pytest.raises(Exception, match="Ошибка при запросе к API: 500"):
            self.synchronizer.get_actors(film_id=123)
    
    def test_get_actors_without_film_id(self):
        with pytest.raises(Exception, match="Необходимо указать film_id для получения актёров"):
            self.synchronizer.get_actors()
    ################################################################################################################################################################
    
    ################################################################ ТЕСТИРУЕМ ИНИЦИАЦИЮ ЗАПРОСА ################################################################
    def test_make_request_success(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        result = self.synchronizer.make_request("http://test.url")
        assert result == {"success": True}
    
    def test_make_request_error(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        
        mocker.patch(
            "requests.get",
            return_value=mock_response
        )
        
        with pytest.raises(Exception, match="Ошибка при запросе к API: 400"):
            self.synchronizer.make_request("http://test.url")
###############################################################################################################################################
