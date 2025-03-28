from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings

import logging
from django.dispatch import receiver
from django.db.models.signals import post_delete


logger = logging.getLogger("kinopoiskapiunofficial_tech_app")


class User(AbstractUser):
    """Класс для пользователей, которые либо являются владельцами конкретной записи в БД, либо нет"""

    is_owner = models.BooleanField(default=False, verbose_name="Владелец записи")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def save(self, *args, **kwargs):
        logger.debug(f"Сохранение записи о пользователе {self.username}, is_owner={self.is_owner}...")
        super().save(*args, **kwargs)
        logger.info(f"Запись о пользователе {self.username} успешно сохранена/обновлена!")


class Film(models.Model):
    """Класс для таблицы с фильмами"""

    kinopoisk_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="ID фильма на стороне API")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год выхода")
    actors = models.ManyToManyField("Actor", related_name="film_actors", blank=True, verbose_name="Персонал")
    created_or_updated_at = models.DateTimeField(auto_now=True, verbose_name="Создано/Обновлено")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="films", verbose_name="Владелец записи")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
    
    def __str__(self):
        return f"{self.name} {self.year}"
    
    def save(self, *args, **kwargs):
        logger.debug(f"Сохранение записи о фильме: {self.name}, kinopoisk_id={self.kinopoisk_id}, owner={self.owner}...")
        super().save(*args, **kwargs)
        logger.info(f"Запись о фильме {self.name} (ID: {self.id}) успешно сохранена/обновлена!")


class Actor(models.Model):
    """Класс для таблицы с актёрами"""
    
    DATE_INPUT_FORMATS = ["%d-%m-%Y"]
    
    staff_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="ID актёра на стороне API")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Имя/Ф.И.О.")
    poster_url = models.URLField(max_length=500, null=True, blank=True, unique=True, verbose_name="Ссылка на постер")
    profession = models.CharField(max_length=255, null=True, blank=True, verbose_name="Профессия/Специальность")
    created_or_updated_at = models.DateTimeField(auto_now=True, verbose_name="Создано/Обновлено")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="actors", verbose_name="Владелец записи")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        logger.debug(f"Сохранение записи об актёрах: {self.name}, staff_id={self.staff_id}, profession={self.profession}, owner={self.owner}...")
        super().save(*args, **kwargs)
        logger.info(f"Запись об актёрах {self.name} (ID: {self.id}) успешно сохранена/обновлена!")


@receiver(post_delete, sender=Film)
def log_film_deletion(sender, instance, **kwargs):
    logger.debug(f"Сигнал 'post_delete' для записи о фильме: {instance.name} (ID: {instance.id})...")
    logger.info(f"Запись о фильме {instance.name} (ID: {instance.id}) удалена!")


@receiver(post_delete, sender=Actor)
def log_actor_deletion(sender, instance, **kwargs):
    logger.debug(f"Сигнал 'post_delete' для записи об актёрах: {instance.name} (ID: {instance.id})")
    logger.info(f"Запись об актёрах {instance.name} (ID: {instance.id}) удалена!")
