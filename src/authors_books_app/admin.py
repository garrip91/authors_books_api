from django.contrib import admin

from .models import Author, Genre, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "date_of_birth", "date_of_death", "owner"]

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "short_description", "isbn", "owner"]
