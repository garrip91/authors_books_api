from django.urls import path
from .views import index, FilmListView, FilmDetailView, ActorListView, ActorDetailView, DownloadFilmsAndActorsByGETMethodView, DownloadFilmsAndActorsByPOSTMethodView


app_name = "main"

urlpatterns = [
    path("", index, name="index"), # страница таблицы с фильмами и актёрами
    
    path("films/", FilmListView.as_view(), name="film-list"), # страница со списком фильмов
    path("films/<int:pk>/", FilmDetailView.as_view(), name="film-detail"),  # страница фильма с искомым id/pk
    
    path("actors/", ActorListView.as_view(), name="actor-list"), # страница со списком актёров
    path("actors/<int:pk>/", ActorDetailView.as_view(), name="actor-detail"),  # страница актёра с искомым id/pk

    path("films-and-actors/download/get/", DownloadFilmsAndActorsByGETMethodView.as_view(), name="download-films-and-actors-by-get-method"),
    path("films-and-actors/download/post/", DownloadFilmsAndActorsByPOSTMethodView.as_view(), name="download-films-and-actors-by-post-method"),
]
