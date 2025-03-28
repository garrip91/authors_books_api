
from django.shortcuts import render
from django.db.models.functions import Cast
from django.db.models import CharField

from rest_framework import generics, permissions, authentication, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from .models import Film, Actor
from .serializers import FilmSerializer, ActorSerializer

from .custom_set_filters.films import FilmFilterSet
from . custom_set_filters.actors import ActorFilterSet

from .custom_permissions import ReadForAllCreateUpdateDeleteForOwnerOrAdmin, AuthenticatedOnly
from .api_sync import APISynchronizer

import logging


logger = logging.getLogger("kinopoiskapiunofficial_tech_app")


def index(request):
    """Функция представления для основной страницы с таблицей фильмов и связанных с ними актёров"""

    logger.debug("Запрос на получение записей о фильмах и актёрах в виде таблицы...")

    films = Film.objects.all()
    actors = Actor.objects.all()
    logger.info(f"Успешно загружено {films.count()} записей о фильмах и {actors.count()} актёрах!")
    
    context = {
        "films": films,
        "actors": actors,
    }
    logger.debug("Контекст для шаблона сформирован!")
    
    return render(request, "kinopoiskapiunofficial_tech_app/index.html", context)


class FilmListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблицы "Film" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/films)"""

    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    filterset_class = FilmFilterSet
    ordering_fields = ("kinopoisk_id", "name", "year", "created_or_updated_at",)
    search_fields = ("kinopoisk_id", "name", "year",)

    def perform_create(self, serializer):
        logger.debug(f"Сохранение новой записи о фильме для пользователя {self.request.user}...")
        serializer.save(owner=self.request.user)
        logger.info(f"Новая запись о фильме сохранена с владельцем {self.request.user}!")

    def get_view_name(self):
        logger.debug("Получение и вывод в шаблоне списка записей DRF заданного названия для фильмов...")
        return "Фильмы"
    
    def get_view_description(self, html=False):
        logger.debug("Получение и вывод в шаблоне списка записей DRF заданного описания для фильмов...")
        return "Страница API с фильмами"


class FilmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Film" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/films/<int:pk>)""" # <int:pk> - это id

    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)

    def perform_create(self, serializer):
        logger.debug(f"Сохранение новой записи о фильме для пользователя {self.request.user}...")
        serializer.save(owner=self.request.user)
        logger.info(f"Новая запись о фильме сохранена с владельцем {self.request.user}!")
    
    def get_view_name(self):
        logger.debug("Получение и вывод в шаблоне одной записи DRF заданного названия для одного фильма...")
        return "Фильм"
    
    def get_view_description(self, html=False):
        logger.debug("Получение и вывод в шаблоне одной записи DRF заданного описания для одного фильма...")
        return "Страница API с конкретным фильмом"

    
class ActorListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблицы "Actor" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/actors)"""

    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    filterset_class = ActorFilterSet
    ordering_fields = ("id", "staff_id", "name", "poster_url", "profession", "created_or_updated_at",)
    search_fields = ("id", "staff_id", "name", "poster_url", "profession",)

    def perform_create(self, serializer):
        logger.debug(f"Сохранение новой записи об актёре для пользователя {self.request.user}...")
        serializer.save(owner=self.request.user)
        logger.info(f"Новая запись об актёре сохранена с владельцем {self.request.user}!")
    
    def get_view_name(self):
        logger.debug("Получение и вывод в шаблоне списка записей DRF заданного названия для актёров...")
        return "Актёры"
    
    def get_view_description(self, html=False):
        logger.debug("Получение и вывод в шаблоне списка записей DRF заданного описания для актёров...")
        return "Страница API с актёрами"


class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Actor" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/actors/<int:pk>)""" # <int:pk> - это id

    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)

    def perform_create(self, serializer):
        logger.debug(f"Сохранение новой записи об актёре для пользователя {self.request.user}...")
        serializer.save(owner=self.request.user)
        logger.info(f"Новая запись об актёре сохранена с владельцем {self.request.user}!")
    
    def get_view_name(self):
        logger.debug("Получение и вывод в шаблоне одной записи DRF заданного названия для актёров, относящихся к одному фильму...")
        return "Актёр"
    
    def get_view_description(self, html=False):
        logger.debug("Получение и вывод в шаблоне одной записи DRF заданного описания для актёров, относящихся к одному фильму...")
        return "Страница API с конкретным актёром"


class DownloadFilmsAndActorsByGETMethodView(APIView):
    
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication,)
    permission_classes = (AuthenticatedOnly,)
    
    def get(self, request):
        """Эндпоинт для загрузки информации о фильмах в базу данных (localhost) через браузер (GET-методом)"""

        logger.debug(f"GET-запрос для синхронизации фильмов и актёров. Пользователь: {request.user}, параметры: {request.GET}")

        try:
            api = APISynchronizer()
            # ПОЛУЧАЕМ ЗНАЧЕНИЕ СТРАНИЦЫ ИЗ GET-ПАРАМЕТРОВ И ПРЕОБРАЗУЕМ ЕГО В ЧИСЛО (int()):
            page = int(request.GET.get("page", 1))
            logger.debug(f"Запуск синхронизации для страницы {page}...")
            result = api.sync_films_and_actors(page=page, user=request.user)
            logger.info(f"Успешно синхронизировано {result['synced_count']} фильмов и актёров. Страница {result['current_page']} из {result['total_pages']}!")
            return Response(
                {
                    "message": f"Информация о {result['synced_count']} фильмах и их актёрах успешно загружена в Вашу базу данных!",
                    "page": result["current_page"],
                    "total_pages": result["total_pages"]
                },
                status=status.HTTP_200_OK
            )
        except ValueError:
            logger.warning(f"Ошибка: параметр 'page' не является числом. Переданное значение: {request.GET.get('page')}!")
            return Response(
                {"error": "Параметр 'page' должен иметь числовое значение!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ошибка при синхронизации фильмов и актёров: {str(e)}!", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
