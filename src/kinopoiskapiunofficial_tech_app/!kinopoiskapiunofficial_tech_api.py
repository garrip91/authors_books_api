import os
import requests
from dotenv import load_dotenv


load_dotenv()

class KinopoiskapiunofficialTechAPI:
    
    BASE_URL_V1 = "https://kinopoiskapiunofficial.tech/api/v1"
    BASE_URL_V2 = "https://kinopoiskapiunofficial.tech/api/v2.2"

    def __init__(self):
        self.headers = {
            "X-API-KEY": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }

    def make_request(self, url):
        """Общий метод для выполнения запросов к API"""
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка при запросе к API: {response.status_code}")

    def get_films(self, film_id=None):
        """Получить информацию о фильме или список фильмов"""
        end_point = "v2.2"
        if film_id:
            url = f"{self.BASE_URL_V2}/films/{film_id}"
        else:
            url = f"{self.BASE_URL_V2}/films"
        return self.make_request(url)

    def get_actors(self, film_id=None, actor_id=None):
        """Получить информацию об актёре или список актёров"""
        end_point = "v1"
        if actor_id:
            url = f"{self.BASE_URL_V1}/staff/{actor_id}"
        elif film_id:
            #url = f"{self.BASE_URL}/staff?filmId={film_id}"
            url = f"{self.BASE_URL_V1}/staff"
            params = {"filmId": film_id}
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ошибка при запросе к API: {response.status_code}")
        else:
            raise ValueError("Необходимо указать film_id или actor_id")
        return self.make_request(url)
    
    def get_all_films_with_actors(self):
        """Получить информацию о фильмах и связанных с ними актёрах"""
        
        films_data = self.get_films() # получаем список всех фильмов
        if not films_data or "items" not in films_data:
            print("Фильмы не найдены!")
            return []
        
        films_with_actors = []
        
        # ПРОХОДИМ ПО КАЖДОМУ ФИЛЬМУ:
        for film in films_data["items"]:
            film_id = film.get("kinopoiskId")
            film_title = film.get("nameRu") or film.get("nameEn")
            
            # ПРОПУСКАЕМ ЗАПИСЬ О ФИЛЬМЕ, ЕСЛИ В НЕЙ ОТСУТСТВУЕТ film_id ИЛИ film_title:
            if not film_id or not film_title:
                print(f"Пропускаем фильм с отсутствующим kinopoiskId: {film}")
                continue
            if not film_title:
                print(f"Пропускаем фильм с отсутствующим названием: {film}")
                continue
            
            print(f"Обрабатываем фильм: {film_title} (ID: {film_id})")
            
            # ПОЛУЧАЕМ СПИСОК АКТЁРОВ ДЛЯ ТЕКУЩЕГО ФИЛЬМА:
            try:
                actors_data = self.get_actors(film_id=film_id)
            except Exception as e:
                print(f"Ошибка при получении актёров для фильма {film_title} (ID: {film_id}): {e}")
                continue

            if not actors_data:
                print(f"Для фильма {film_title} (ID: {film_id}) актёры не найдены!") # TODO
                continue

            actors_list = [] # список для хранения данных об актёрах
            
            # ОБРАБАТЫВАЕМ КАЖДОГО АКТЁРА:
            for actor_data in actors_data:
                actor_id = actor_data.get("staffId")
                actor_name = actor_data.get("nameRu") or actor_data.get("nameEn")

                # ПРОПУСКАЕМ ЗАПИСЬ ОБ АКТЁРЕ, ЕСЛИ У НЕГО ОТСУТСТВУЕТ actor_id ИЛИ actor_name:
                if not actor_id or not actor_name:
                    print(f"Пропускаем актёра с некорректными данными: {actor_data}")
                    continue

                # ДОБАВЛЯЕМ АКТЁРА В СПИСОК:
                actors_list.append({
                    "person_id": actor_id,
                    "name": actor_name,
                    "profession": actor_data.get("professionText"),
                    "poster_url": actor_data.get("posterUrl"),
                    ###### ЗДЕСЬ ДОБАВИТЬ ОСТАЛЬНЫЕ НУЖНЫЕ ПОЛЯ ######
                })

            # ДОБАВЛЯЕМ ФИЛЬМ И ЕГО АКТЁРОВ В ОБЩИЙ СПИСОК:
            films_with_actors.append({
                "film_id": film_id,
                "title": film_title,
                "year": film.get("year"),
                "poster_url": film.get("posterUrl"),
                "actors": actors_list,
                ###### ЗДЕСЬ ДОБАВИТЬ ОСТАЛЬНЫЕ НУЖНЫЕ ПОЛЯ ######
            })

        print("Все фильмы и актёры успешно обработаны!")
        return films_with_actors


api = KinopoiskapiunofficialTechAPI()

#films_data = api.get_films()
#print(f"****[[ {films_data} ]]****")

#actors_data = api.get_actors(film_id=66539)
#print(f"****[[ {actors_data} ]]")

#films_with_actors_data = api.get_all_films_with_actors()
#print(f"****[[ {films_with_actors_data} ]]****")
