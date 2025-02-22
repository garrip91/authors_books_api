from django.urls import path
from .views import index
from .views import index, AuthorViewSet, GenreViewSet, BookViewSet


app_name = "authors_books_app"

urlpatterns = [
    #path("index/", index, name="index"),
    path("", index, name="index"),
]
