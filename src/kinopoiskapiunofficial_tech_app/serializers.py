import json
from rest_framework import serializers
from .models import Film, Actor


class FilmSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Film в формат json"""

    kinopoisk_id = serializers.IntegerField(required=False, allow_null=True, label="ID фильма на сайте")
    name = serializers.CharField(allow_null=True, allow_blank=True, required=False, label="Название")
    year = serializers.IntegerField(allow_null=True, required=False, label="Год выхода")
    actors = serializers.SerializerMethodField(allow_null=True, required=False, label="Актёры") # для отображения строкового представления поля actors
    created_or_updated_at_formatted = serializers.SerializerMethodField()

    def get_actors(self, obj):
        """
        Возвращает строковое представление поля actors.
        Также исключает проблему с циклической зависимостью между классами FilmSerializer и ActorSerializer.
        """
        actors = obj.actors.all()
        return [{"id": actor.id, "name": actor.name} for actor in actors]
    
    def get_created_or_updated_at_formatted(self, obj):
        return obj.created_or_updated_at.strftime("%d.%m.%Y | %H:%M:%S")

    class Meta:
        model = Film
        fields = ("id", "kinopoisk_id", "name", "year", "actors", "created_or_updated_at", "created_or_updated_at_formatted",)
        read_only_fields = ("created_or_updated_at",)


class ActorSerializer(serializers.ModelSerializer):
    """Класс-сериализатор, используемый для преобразования объектов модели Actor в формат json"""

    staff_id = serializers.IntegerField(required=False, allow_null=True, label="ID актёра на стороне API")
    name = serializers.CharField(allow_null=True, allow_blank=True, required=False, label="Имя/Ф.И.О.")
    poster_url = serializers.URLField(max_length=500, allow_null=True, allow_blank=True, required=False, label="Постер")
    profession = serializers.CharField(allow_null=True, allow_blank=True, required=False, label="Профессия/Специальность")
    created_or_updated_at_formatted = serializers.SerializerMethodField()
    
    def get_created_or_updated_at_formatted(self, obj):
        return obj.created_or_updated_at.strftime("%d.%m.%Y | %H:%M:%S")
    
    class Meta:
        model = Actor
        fields = ("id", "staff_id", "name", "poster_url", "profession", "created_or_updated_at", "created_or_updated_at_formatted",)
        read_only_fields = ("created_or_updated_at",)

