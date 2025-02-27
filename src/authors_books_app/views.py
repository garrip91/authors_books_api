from django.shortcuts import render

from rest_framework import permissions, viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Genre, Book
from .serializers import AuthorSerializer, GenreSerializer, BookSerializer, AllDataSerializer

from . custom_set_filters.authors import AuthorFilterSet
from . custom_set_filters.books import BookFilterSet
from . custom_set_filters.genres import GenreFilterSet

from . import custom_permissions 


def index(request):
    """Функция представления для основной страницы с таблицей авторов, жанров, книг и не только..."""

    authors = Author.objects.all()
    genres = Genre.objects.all()
    books = Book.objects.all()

    zipped_data = zip(authors, books) # упаковываем модель авторов и модель книг в zip() для их совместного отображения в одной видимой таблице на странице index.html
    zipped_data_list = list(zipped_data) # преобразуем наш zip() в список для лучшего отображения в консоли
    
    context = {
        "zipped_data": zipped_data_list,
        "genres": genres,
    }
    
    return render(request, "authors_books_app/index.html", context)
    

class AuthorListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблицы "Author" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/authors)"""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    filterset_class = AuthorFilterSet
    ordering_fields = ("first_name", "last_name", "date_of_birth", "date_of_death",)
    search_fields = (
        "first_name",
        "last_name",
        "date_of_birth",
        "date_of_death",
    )

    def get_view_name(self):
        return "Авторы"
    
    def get_view_description(self, html=False):
        return "Страница API с авторами книг"
    
    # НАЗНАЧАЕМ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ВЛАДЕЛЬЦЕМ ЗАПИСИ ПРИ ЕЁ СОЗДАНИИ:
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Author" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/authors/<int:pk>)""" # <int:pk> - это id

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, custom_permissions.IsOwnerOrReadOnly,)

    def get_view_name(self):
        return "Автор"
    
    def get_view_description(self, html=False):
        return "Страница API с автором конкретной книги"


class GenreViewSet(viewsets.ModelViewSet):
    
    queryset = Genre.objects.all().order_by("id")
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, custom_permissions.IsOwnerOrReadOnly]

    def get_view_name(self):
        return "Жанры"
    
    def get_view_description(self, html=False):
        return "Страница API с жанрами книг"
    
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = GenreFilterSet
    ordering_fields = ["name"]
    search_fields = [
        "name",
    ]

    # НАЗНАЧАЕМ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ВЛАДЕЛЬЦЕМ ЗАПИСИ ПРИ ЕЁ СОЗДАНИИ:
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    # НАСТРАИВАЕМ ПРАВА ДОСТУПА:
    # В этом методе мы возвращаем записи только текущего пользователя:
    def get_queryset(self):
        if self.action in ["list", "retrieve"]:              # для "безопасных" действий, а именно: `list` (просмотр списка объектов) и `retrieve` (просмотр деталей объекта)...
            return Genre.objects.all()                       # ...со стороны текущего пользователя мы возвращаем ему полный набор записей из соответствующей таблицы БД,...
        return Genre.objects.filter(owner=self.request.user) # ...а для "НЕбезопасных" действий (то есть, всех остальных self.actions) с его стороны мы возвращаем ему только свои записи из этой самой таблицы
    

class GenreListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблицы "Genre" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/genres)"""

    pass


class GenreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Genre" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/genres/<int:pk>)""" # <int:pk> - это id

    pass


class BookViewSet(viewsets.ModelViewSet):
    
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, custom_permissions.IsOwnerOrReadOnly]

    def get_view_name(self):
        return "Книги"
    
    def get_view_description(self, html=False):
        return "Страница API с книгами"
    
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = BookFilterSet
    ordering_fields = ["title", "author", "short_description", "genre", "isbn"]
    search_fields = [
        "title",
        "author__first_name",
        "author__last_name",
        "short_description",
        "genre__name",
        "isbn",
    ]

    # НАЗНАЧАЕМ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ВЛАДЕЛЬЦЕМ ЗАПИСИ ПРИ ЕЁ СОЗДАНИИ:
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    # НАСТРАИВАЕМ ПРАВА ДОСТУПА:
    # В этом методе мы возвращаем записи только текущего пользователя:
    def get_queryset(self):
        if self.action in ["list", "retrieve"]:             # для "безопасных" действий, а именно: `list` (просмотр списка объектов) и `retrieve` (просмотр деталей объекта)...
            return Book.objects.all()                       # ...со стороны текущего пользователя мы возвращаем ему полный набор записей из соответствующей таблицы БД,...
        return Book.objects.filter(owner=self.request.user) # ...а для "НЕбезопасных" действий (то есть, всех остальных self.actions) с его стороны мы возвращаем ему только свои записи из этой самой таблицы
    

class BookListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблицы "Book" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/books)"""

    pass


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Класс обработки запросов и возврата ответов для запрошенной по id записи из таблицы "Book" подключённой БД с её последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/books/<int:pk>)""" # <int:pk> - это id

    pass


class AllDataViewSet(viewsets.ViewSet):
    
    serializer_class = AllDataSerializer
    
    def list(self, request):
        authors = Author.objects.all()
        genres = Genre.objects.all()
        books = Book.objects.all()

        serializer = self.get_serializer({
            "authors": authors,
            "genres": genres,
            "books": books,
        })

        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)
    
    def get_view_name(self):
        return "Авторы, жанры и книги"
    
    def get_view_description(self, html=False):
        return "Страница API с авторами, жанрами и книгами"


class AllDataListView(generics.ListCreateAPIView):
    """Класс обработки запросов и возврата ответов для всех записей из таблиц "Author", "Genre" и "Book" подключённой БД с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/v1/all-data)"""

    pass
