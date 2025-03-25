from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Класс для пользователей, которые либо являются владельцами конкретной записи в БД, либо нет"""

    is_owner = models.BooleanField(default=False, verbose_name="Владелец")


class Film(models.Model):
    """Класс для таблицы с фильмами"""

    kinopoisk_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="ID фильма на стороне API")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год выхода")
    actors = models.ManyToManyField("Actor", related_name="film_actors", blank=True, verbose_name="Персонал")
    created_or_updated_at = models.DateTimeField(auto_now=True, verbose_name="Создано/Обновлено")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
    
    def __str__(self):
        return f"{self.name} {self.year}"


class Actor(models.Model):
    """Класс для таблицы с актёрами"""
    
    DATE_INPUT_FORMATS = ["%d-%m-%Y"]
    
    staff_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="ID актёра на стороне API")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Имя/Ф.И.О.")
    poster_url = models.URLField(max_length=500, null=True, blank=True, unique=True, verbose_name="Ссылка на постер")
    profession = models.CharField(max_length=255, null=True, blank=True, verbose_name="Профессия/Специальность")
    created_or_updated_at = models.DateTimeField(auto_now=True, verbose_name="Создано/Обновлено")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"
    
    def __str__(self):
        return self.name
