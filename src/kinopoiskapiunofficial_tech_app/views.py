
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


def index(request):
    """Функция представления для основной страницы с таблицей авторов, жанров, книг и не только..."""

    films = Film.objects.all().prefetch_related("actors")
    actors = Actor.objects.all().prefetch_related("films")
    
    context = {
        "films": films,
        "actors": actors,
    }
    
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
        serializer.save(owner=self.request.user)

    def get_view_name(self):
        return "Фильмы"
    
    def get_view_description(self, html=False):
        return "Страница API с фильмами"


class FilmDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Film" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/films/<int:pk>)""" # <int:pk> - это id

    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_view_name(self):
        return "Фильм"
    
    def get_view_description(self, html=False):
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
        serializer.save(owner=self.request.user)
    
    def get_view_name(self):
        return "Актёры"
    
    def get_view_description(self, html=False):
        return "Страница API с актёрами"


class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Actor" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/actors/<int:pk>)""" # <int:pk> - это id

    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (ReadForAllCreateUpdateDeleteForOwnerOrAdmin,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_view_name(self):
        return "Актёр"
    
    def get_view_description(self, html=False):
        return "Страница API с конкретным актёром"


class DownloadFilmsAndActorsByGETMethodView(APIView):
    
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication,)
    permission_classes = (AuthenticatedOnly,)
    
    def get(self, request):
        """Эндпоинт для загрузки информации о фильмах в базу данных (localhost) через браузер (GET-методом)"""

        try:
            api = APISynchronizer()
            # ПОЛУЧАЕМ ЗНАЧЕНИЕ СТРАНИЦЫ ИЗ GET-ПАРАМЕТРОВ И ПРЕОБРАЗУЕМ ЕГО В ЧИСЛО (int()):
            page = int(request.GET.get("page", 1))
            result = api.sync_films_and_actors(page=page, user=request.user)
            return Response(
                {
                    "message": f"Информация о {result['synced_count']} фильмах и их актёрах успешно загружена в Вашу базу данных!",
                    "page": result["current_page"],
                    "total_pages": result["total_pages"]
                },
                status=status.HTTP_200_OK
            )
        except ValueError:
            return Response(
                {"error": "Параметр 'page' должен иметь числовое значение!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DownloadFilmsAndActorsByPOSTMethodView(DownloadFilmsAndActorsByGETMethodView):
    
    def post(self, request):
        """Эндпоинт для загрузки информации о фильмах в базу данных (localhost) (POST-методом)"""

        try:
            api = APISynchronizer()
            # ПОЛУЧАЕМ СТРАНИЦУ ИЗ POST-ПАРАМЕТРОВ:
            page = request.POST.get("page", 1)
            result = api.sync_films_and_actors(page=page, user=request.user)
            return Response(
                {
                    "message": f"Информация о {result['synced_count']} фильмах и их актёрах успешно загружена в Вашу базу данных!",
                    "page": result["current_page"],
                    "total_pages": result["total_pages"]
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
