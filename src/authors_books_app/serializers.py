from rest_framework import serializers
from .models import Author, Genre, Book


#class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class AuthorSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Author в формат json"""

    class Meta:
        model = Author
        fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]


#class GenreSerializer(serializers.HyperlinkedModelSerializer):
class GenreSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Genre в формат json"""

    class Meta:
        model = Genre
        fields = ["name"]


#class BookSerializer(serializers.HyperlinkedModelSerializer):
class BookSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Book в формат json"""
    
    class Meta:
        model = Book
        fields = ["title", "author", "short_description", "genre", "isbn"]


class AllDataSerializer(serializers.Serializer):
    """Класс-сериализатор, охватывающий преобразования объектов моделей Author, Genre и Book в формат json (в виде единого целого)"""
    
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)
    books = BookSerializer(many=True)
