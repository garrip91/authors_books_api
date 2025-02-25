from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User


class Author(models.Model):
    """Класс для таблицы с авторами"""
    
    DATE_INPUT_FORMATS = ["%d-%m-%Y"]

    first_name = models.CharField(max_length=100, help_text="Укажите здесь имя автора", verbose_name="Имя")
    last_name = models.CharField(max_length=100, help_text="Укажите здесь фамилию автора", verbose_name="Фамилия", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, help_text="Укажите здесь дату рождения автора", verbose_name="Дата рождения")
    date_of_death = models.DateField(help_text="Укажите здесь дату смерти автора", verbose_name="Дата смерти", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True)
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    """Класс для таблицы с жанрами"""
    
    name = models.CharField(max_length=200, help_text="Укажите здесь название жанра книги", verbose_name="Название жанра")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True)
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Класс для таблицы с книгами"""
    
    title = models.CharField(max_length=200, help_text="Укажите здесь название книги", verbose_name="Название")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True, help_text="Выберите здесь автора книги", verbose_name="Автор")
    short_description = models.TextField(max_length=1000, help_text="Укажите здесь краткое описание книги", verbose_name="Краткое описание")
    genre = models.ManyToManyField(Genre, help_text="Выберите здесь жанр книги", verbose_name="Жанр")
    isbn = models.CharField(max_length=20, help_text="Укажите здесь ISBN книги", verbose_name="ISBN", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True)
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
    
    def __str__(self):
        return self.title
