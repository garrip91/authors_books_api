import os
import requests
from dotenv import load_dotenv
from .models import Film, Actor
from .serializers import FilmSerializer, ActorSerializer


load_dotenv()

class APISynchronizer:

    BASE_URL_V1 = "https://kinopoiskapiunofficial.tech/api/v1"
    BASE_URL_V2 = "https://kinopoiskapiunofficial.tech/api/v2.2"

    def __init__(self):
        self.headers = {
            "X-API-KEY": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }

    def make_request(self, url, params=None):
        """Общий метод для выполнения запросов к API"""
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка при запросе к API: {response.status_code}")

    def get_films(self, page=1):
        """Получаем информацию о фильме или список фильмов"""
        url = f"{self.BASE_URL_V2}/films"
        params = {
            "page": page,
        }
        return self.make_request(url, params=params)

    def get_actors(self, film_id=None):
        """Получаем информацию об актёре (или список актёров) по фильму"""
        if not film_id:
            raise Exception("Необходимо указать film_id для получения актёров")
        url = f"{self.BASE_URL_V1}/staff"
        params = {
            "filmId": film_id
        }
        return self.make_request(url, params=params)
    
    def sync_films_and_actors(self, page=1, user=None):
        """Актуализируем всю информацию в своей БД путём синхронизации"""

        # ПОЛУЧАЕМ ПЕРВИЧНЫЕ ДАННЫЕ (ЗАПИСИ) О ФИЛЬМАХ:
        api_data = self.get_films(page)
        films_data = api_data.get("items", [])
        
        # ФОРМАТИРУЕМ ПОЛУЧЕННЫЕ ДАННЫЕ:
        films_formatted_data = [
            {
             "kinopoisk_id": film.get("kinopoiskId"),
             "name": film.get("nameRu") or film.get("nameOriginal") or "Без названия",
             "year": film.get("year"),
             #"owner": user.id if user else None
            }
            for film in films_data
        ]

        # ВАЛИДИРУЕМ ИНФОРМАЦИЮ О ФИЛЬМАХ ЧЕРЕЗ СЕРИАЛИЗАТОР:
        film_serializer = FilmSerializer(
            data=films_formatted_data,
            many=True
        )
        film_serializer.is_valid(raise_exception=True)
        
        synced_films = []
        for film_data in film_serializer.validated_data:
            kinopoisk_id = film_data["kinopoisk_id"]
            # СОЗДАЁМ ИЛИ ОБНОВЛЯЕМ (В СЛУЧАЕ НАЛИЧИЯ) ЗАПИСЬ О ФИЛЬМЕ ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ (ПОКА ЧТО БЕЗ ИНФОРМАЦИИ ОБ АКТЁРАХ):
            film, created = Film.objects.update_or_create(
                kinopoisk_id=kinopoisk_id,
                defaults={
                    "name": film_data["name"],
                    "year": film_data["year"],
                    #"owner": user
                }
            )
            synced_films.append(film)
            
            # ПЫТАЕМСЯ ПОЛУЧИТЬ И СИНХРОНИЗИРОВАТЬ ИНФОРМАЦИЮ ОБ АКТЁРАХ ДЛЯ ЗАПИСИ ФИЛЬМА ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
            try:
                actors_data = self.get_actors(film_id=kinopoisk_id)
                actors_formatted_data = [
                    {
                        "staff_id": actor.get("staffId"),
                        "name": actor.get("nameRu"),
                        "poster_url": actor.get("posterUrl"),
                        "profession": actor.get("professionText"),
                        #"owner": user.id if user else None
                    }
                    for actor in actors_data
                ]

                # ВАЛИДИРУЕМ ИНФОРМАЦИЮ ОБ АКТЁРАХ ЧЕРЕЗ СЕРИАЛИЗАТОР:
                actor_serializer = ActorSerializer(
                    data=actors_formatted_data,
                    many=True
                )
                actor_serializer.is_valid(raise_exception=True)
                
                # ОЧИЩАЕМ ВСЮ УЖЕ ИМЕЮЩУЮСЯ В НАШЕЙ БД ИНФОРМАЦИЮ ОБ АКТЁРАХ, ОТНОСЯЩИХСЯ К ЗАПИСИ ФИЛЬМА ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
                film.actors.clear()

                # СОЗДАЁМ ЛИБО ОБНОВЛЯЕМ ЗАПИСИ ОБ АКТЁРАХ И ДОБАВЛЯЕМ ИХ В ЗАПИСЬ О ФИЛЬМЕ ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
                for actor_data in actor_serializer.validated_data:
                    actor, created = Actor.objects.update_or_create(
                        staff_id=actor_data["staff_id"],
                        defaults={
                            "name": actor_data["name"],
                            "poster_url": actor_data["poster_url"],
                            "profession": actor_data["profession"],
                            #"owner": user
                        }
                    )
                    film.actors.add(actor)

            except Exception as e:
                print(f"Ошибка при загрузке актёров для фильма {kinopoisk_id}: {e}")
                continue

        return {
            "synced_count": len(synced_films),
            "total_pages": api_data.get("totalPages", 1),
            "current_page": page
        }
