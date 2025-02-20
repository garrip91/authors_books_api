from django.db import models


class Author(models.Model):
    """Класс для таблицы с авторами"""
    
    first_name = models.CharField(max_length=100, help_text="Укажите здесь имя автора")
    last_name = models.CharField(max_length=100, help_text="Укажите здесь фамилию автора")
    date_of_birth = models.DateField(blank=True, null=True, help_text="Укажите здесь дату рождения автора")
    #date_of_death = models.DateField(default="Скончался", blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True, help_text="Укажите здесь дату смерти автора")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    """Класс для таблицы с жанрами"""
    
    name = models.CharField(max_length=200, help_text="Укажите здесь жанр книги")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Класс для таблицы с книгами"""
    
    title = models.CharField(max_length=200, help_text="Укажите здесь название книги")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True, help_text="Выберите здесь автора книги")
    short_description = models.TextField(max_length=1000, help_text="Укажите здесь краткое описание книги")
    genre = models.ManyToManyField(Genre, help_text="Выберите здесь жанр книги")
    #isbn = models.CharField(default="ISBN", max_length=20, help_text="https://ru.wikipedia.org/wiki/%D0%9C%D0%B5%D0%B6%D0%B4%D1%83%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D1%8B%D0%B9_%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D1%8B%D0%B9_%D0%BA%D0%BD%D0%B8%D0%B6%D0%BD%D1%8B%D0%B9_%D0%BD%D0%BE%D0%BC%D0%B5%D1%80")
    isbn = models.CharField(max_length=20, blank=True, null=True, help_text="Укажите здесь ISBN книги")
    
    class Meta:
        ordering = ("id",)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
    
    def __str__(self):
        return self.title
