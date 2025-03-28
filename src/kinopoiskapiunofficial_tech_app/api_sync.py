import os
import requests
from dotenv import load_dotenv
from .models import Film, Actor
from .serializers import FilmSerializer, ActorSerializer

import logging


logger = logging.getLogger("kinopoiskapiunofficial_tech_app")


load_dotenv()

class APISynchronizer:

    BASE_URL_V1 = "https://kinopoiskapiunofficial.tech/api/v1"
    BASE_URL_V2 = "https://kinopoiskapiunofficial.tech/api/v2.2"

    def __init__(self):
        self.headers = {
            "X-API-KEY": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }
        logger.debug("Инициализация APISynchronizer с заголовками...")

    def make_request(self, url, params=None):
        """Общий метод для выполнения запросов к API"""
        logger.debug(f"Запрос к API: {url}, параметры: {params}...")
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            logger.debug(f"Успешный ответ от API: {url}, статус-код: {response.status_code}!")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к API с URL - {url}: {str(e)}!", exc_info=True)
            raise Exception(f"Ошибка при запросе к API: {response.status_code if 'response' in locals() else 'НЕИЗВЕСТНО'}!")

    def get_films(self, page=1):
        """Получаем информацию о фильме или список фильмов"""
        url = f"{self.BASE_URL_V2}/films"
        params = {
            "page": page,
        }
        logger.debug(f"Получение записей о фильмах, страница: {page}...")
        try:
            data = self.make_request(url, params)
            logger.info(f"Успешно получено {len(data.get('items', []))} записей о фильмах со страницы {page}!")
            return data
        except Exception as e:
            logger.error(f"Ошибка при получении записей о фильмах со страницы {page}: {str(e)}!", exc_info=True)
            raise

    def get_actors(self, film_id=None):
        """Получаем информацию об актёре (или список актёров) по фильму"""
        if not film_id:
            logger.warning("Попытка получить записи об актёрах без указания 'film_id'...")
            raise Exception("Необходимо указать film_id для получения актёров")
        url = f"{self.BASE_URL_V1}/staff"
        params = {
            "filmId": film_id
        }
        logger.debug(f"Получение записи об актёрах для фильма с ID {film_id}...")
        try:
            data = self.make_request(url, params=params)
            logger.info(f"Успешно получено {len(data)} записей об актёрах для фильма с ID {film_id}!")
            return data
        except Exception as e:
            logger.error(f"Ошибка при получении записей об актёрах для фильма с ID {film_id}: {str(e)}!", exc_info=True)
            raise
    
    def sync_films_and_actors(self, page=1, user=None):
        """Актуализируем всю информацию в своей БД путём синхронизации"""

        logger.debug(f"Начало синхронизации записей о фильмах и актёрах, страница: {page}, пользователь: {user}...")
        try:

            # ПОЛУЧАЕМ ПЕРВИЧНЫЕ ДАННЫЕ (ЗАПИСИ) О ФИЛЬМАХ:
            api_data = self.get_films(page)
            films_data = api_data.get("items", [])
        
            # ФОРМАТИРУЕМ ПОЛУЧЕННЫЕ ДАННЫЕ:
            films_formatted_data = [
                {
                    "kinopoisk_id": film.get("kinopoiskId"),
                    "name": film.get("nameRu") or film.get("nameOriginal") or "Без названия",
                    "year": film.get("year"),
                }
                for film in films_data
            ]
            logger.debug(f"Подготовлено {len(films_formatted_data)} записей о фильмах для сериализации!")

            # ВАЛИДИРУЕМ ИНФОРМАЦИЮ О ФИЛЬМАХ ЧЕРЕЗ СЕРИАЛИЗАТОР:
            film_serializer = FilmSerializer(
                data=films_formatted_data,
                many=True
            )
            film_serializer.is_valid(raise_exception=True)
            logger.debug("Валидация записей о фильмах прошла успешно!")
            
            synced_films = []
            for film_data in film_serializer.validated_data:
                kinopoisk_id = film_data["kinopoisk_id"]
                logger.debug(f"Обработка записи о фильме с kinopoisk_id: {kinopoisk_id}...")
                # СОЗДАЁМ ИЛИ ОБНОВЛЯЕМ (В СЛУЧАЕ НАЛИЧИЯ) ЗАПИСЬ О ФИЛЬМЕ ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ (ПОКА ЧТО БЕЗ ИНФОРМАЦИИ ОБ АКТЁРАХ):
                film, created = Film.objects.update_or_create(
                    kinopoisk_id=kinopoisk_id,
                    defaults={
                        "name": film_data["name"],
                        "year": film_data["year"],
                    }
                )
                synced_films.append(film)
                logger.info(f"Запись о фильме {film.name} (kinopoisk_id: {kinopoisk_id}) {'создана' if created else 'обновлена'}!")
                
                # ПЫТАЕМСЯ ПОЛУЧИТЬ И СИНХРОНИЗИРОВАТЬ ИНФОРМАЦИЮ ОБ АКТЁРАХ ДЛЯ ЗАПИСИ ФИЛЬМА ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
                try:
                    actors_data = self.get_actors(film_id=kinopoisk_id)
                    actors_formatted_data = [
                        {
                            "staff_id": actor.get("staffId"),
                            "name": actor.get("nameRu"),
                            "poster_url": actor.get("posterUrl"),
                            "profession": actor.get("professionText"),
                        }
                        for actor in actors_data
                    ]
                    logger.debug(f"Подготовлено {len(actors_formatted_data)} записей об актёрах для фильма {kinopoisk_id}!")

                    # ВАЛИДИРУЕМ ИНФОРМАЦИЮ ОБ АКТЁРАХ ЧЕРЕЗ СЕРИАЛИЗАТОР:
                    actor_serializer = ActorSerializer(
                        data=actors_formatted_data,
                        many=True
                    )
                    actor_serializer.is_valid(raise_exception=True)
                    logger.debug(f"Валидация записей об актёрах для фильма {kinopoisk_id} прошла успешно!")
                    
                    # ОЧИЩАЕМ ВСЮ УЖЕ ИМЕЮЩУЮСЯ В НАШЕЙ БД ИНФОРМАЦИЮ ОБ АКТЁРАХ, ОТНОСЯЩИХСЯ К ЗАПИСИ ФИЛЬМА ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
                    film.actors.clear()
                    logger.debug(f"Очищены имеющиеся в БД записи об актёрах для фильма {kinopoisk_id}!")

                    # СОЗДАЁМ ЛИБО ОБНОВЛЯЕМ ЗАПИСИ ОБ АКТЁРАХ И ДОБАВЛЯЕМ ИХ В ЗАПИСЬ О ФИЛЬМЕ ИЗ ТЕКУЩЕЙ ИТЕРАЦИИ:
                    for actor_data in actor_serializer.validated_data:
                        actor, created = Actor.objects.update_or_create(
                            staff_id=actor_data["staff_id"],
                            defaults={
                                "name": actor_data["name"],
                                "poster_url": actor_data["poster_url"],
                                "profession": actor_data["profession"],
                            }
                        )
                        film.actors.add(actor)
                        logger.info(f"Запись об актёре {actor.name} (staff_id: {actor_data['staff_id']}) {'добавлена к записи о фильме' if created else 'обновлена'} {kinopoisk_id}!")

                except Exception as e:
                    logger.error(f"Ошибка при загрузке записей об актёрах для фильма {kinopoisk_id}: {str(e)}!", exc_info=True)
                    continue

            result = {
                "synced_count": len(synced_films),
                "total_pages": api_data.get("totalPages", 1),
                "current_page": page
            }
            logger.info(f"Синхронизация завершена: {result['synced_count']} записей о фильмах, страница {page} из {result['total_pages']}!")
            return result
        
        except Exception as e:
            logger.error(f"Ошибка при синхронизации записей о фильмах и актёрах на странице {page}: {str(e)}!", exc_info=True)
            raise
