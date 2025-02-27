from django.urls import path
from .views import index
from .views import index, AuthorListView, AuthorDetailView, GenreListView, GenreDetailView, BookListView, BookDetailView, AllDataListView


app_name = "main"

urlpatterns = [
    path("", index, name="index"), # страница таблицы с авторами, жанрами, книгами и не только...
    
    path("authors/", AuthorListView.as_view(), name="author-list"), # страница со списком авторов
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),  # страница автора с искомым id/pk
    
    path("genres/", GenreListView.as_view(), name="genre-list"), # страница со списком жанров
    path("genres/<int:pk>/", GenreDetailView.as_view(), name="genre-detail"),  # страница жанра с искомым id/pk

    path("books/", BookListView.as_view(), name="book-list"), # страница со списком книг
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),  # страница книги с искомым id/pk
    
    path("all-data/", AllDataListView.as_view(), name="all-data-list"), # страница со списком авторов, жанров и книг
]
