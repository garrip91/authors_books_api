from django.shortcuts import render
# from django.views.generic import TemplateView
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Author, Genre, Book
from .serializers import AuthorSerializer, GenreSerializer, BookSerializer, AllDataSerializer


# class IndexView(TemplateView):
#     #template_name = "AuthorsBooksDRFApp/index.html"
#     template_name = "index.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         #context["title"] = "Метатег <title>"
#         #context["content"] = "Метатег <content>"
#         return context


def index(request):
    """Функция представления для основной страницы с авторами и их книгами"""

    authors = Author.objects.all()
    genres = Genre.objects.all()
    books = Book.objects.all()

    zipped_data = zip(authors, books) # упаковываем модель авторов и модель книг в zip() для их совместного отображения в одной видимой таблице на странице index.html
    zipped_data_list = list(zipped_data) # преобразуем наш zip() в список для лучшего отображения в консоли
    print(zipped_data_list) # отображаем наш полученный список в консоли 
    
    context = {
        "zipped_data": zipped_data_list,
        "genres": genres,
    }
    
    return render(request, "authors_books_app/index.html", context)


class AuthorViewSet(viewsets.ModelViewSet):
    """Класс обработки запросов и возврата ответов ДЛЯ АВТОРОВ с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/authors/)"""
    
    queryset = Author.objects.all().order_by("id")
    serializer_class = AuthorSerializer
    #permission_classes = [permissions.IsAuthenticated]
    #name = "Авторы"

    def get_view_name(self):
        return "Авторы"
    
    def get_view_description(self, html=False):
        return "Страница API с авторами книг"


class GenreViewSet(viewsets.ModelViewSet):
    """Класс обработки запросов и возврата ответов ДЛЯ ЖАНРОВ с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/genres/)"""
    
    queryset = Genre.objects.all().order_by("id")
    serializer_class = GenreSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_view_name(self):
        return "Жанры"
    
    def get_view_description(self, html=False):
        return "Страница API с жанрами книг"


class BookViewSet(viewsets.ModelViewSet):
    """Класс обработки запросов и возврата ответов ДЛЯ КНИГ с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/books/)"""
    
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_view_name(self):
        return "Книги"
    
    def get_view_description(self, html=False):
        return "Страница API с книгами"


class AllDataViewSet(viewsets.ViewSet):
    """Класс обработки запросов и возврата ответов ДЛЯ ВСЕХ ОБЪЕКТОВ/СУЩНОСТЕЙ с их последующей передачей на соответствующую страницу (в данном случае это localhost/api/all-data/)"""
    
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
