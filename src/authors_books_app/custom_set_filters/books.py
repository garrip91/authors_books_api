from django.db.models import Q
from django_filters import rest_framework as filters

from ..models import Book


class BookFilterSet(filters.FilterSet):
    """Класс для фильтрации книг по критериям"""
    
    title = filters.CharFilter(lookup_expr="icontains", label="Название") # поиск по части слова и без учёта регистра
    author = filters.CharFilter(method="filter_by_author", label="Автор")
    short_description = filters.CharFilter(lookup_expr="icontains", label="Краткое описание") # поиск по части слова и без учёта регистра
    #genre = filters.CharFilter(lookup_expr="icontains", label="Жанр") # поиск по части слова и без учёта регистра
    genre = filters.CharFilter(field_name="genre__name", lookup_expr="icontains", label="Жанр")
    isbn = filters.CharFilter(lookup_expr="icontains", label="ISBN") # поиск по части слова и без учёта регистра

    def filter_by_author(self, queryset, name, value):
        """Кастомный метод для поиска авторов как по полю `first_name`, так и по полю `last_name`"""
        return queryset.filter(
            Q(author__first_name__icontains=value) | Q(author__last_name__icontains=value)
        )
    
    class Meta:
        model = Book
        fields = ("title", "author", "short_description", "genre", "isbn",)
