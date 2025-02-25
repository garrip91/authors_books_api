from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Author, Genre, Book


#class AuthorSerializer(serializers.HyperlinkedModelSerializer):
class AuthorSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Author в формат json"""

    first_name = serializers.CharField(label="Имя")
    last_name = serializers.CharField(required=False, allow_null=True, label="Фамилия")

    # ФОРМАТЫ ВВОДА И ВЫВОДА ДАТ ДЛЯ ЛИЦ, ПРИВЫКШИХ К `ДД.ММ.ГГГГ`:
    date_of_birth = serializers.DateField(input_formats=["%Y-%m-%d", "%d.%m.%Y"], label="Дата рождения")
    date_of_death = serializers.DateField(required=False, allow_null=True, input_formats=["%Y-%m-%d", "%d.%m.%Y"], label="Дата смерти")
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), label="Владелец")

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "date_of_birth", "date_of_death", "owner"]


#class GenreSerializer(serializers.HyperlinkedModelSerializer):
class GenreSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Genre в формат json"""

    name = serializers.CharField(label="Название")
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), label="Владелец")

    class Meta:
        model = Genre
        fields = ["id", "name", "owner"]


#class BookSerializer(serializers.HyperlinkedModelSerializer):
class BookSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Book в формат json"""
    
    title = serializers.CharField(label="Название")
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), label="Автор")
    short_description = serializers.CharField(label="Краткое описание")
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True, label="Жанр")
    isbn = serializers.CharField(label="ISBN")
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), label="Владелец")

    class Meta:
        model = Book
        fields = ["id", "title", "author", "short_description", "genre", "isbn", "owner"]


class AllDataSerializer(serializers.Serializer):
    """Класс-сериализатор, охватывающий преобразования объектов моделей Author, Genre и Book в формат json (в виде единого целого)"""
    
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)
    books = BookSerializer(many=True)
