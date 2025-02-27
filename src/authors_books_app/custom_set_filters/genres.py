from django_filters import rest_framework as filters

from ..models import Genre


class GenreFilterSet(filters.FilterSet):
    """Класс для фильтрации книг по критериям"""
    
    name = filters.CharFilter(lookup_expr="icontains", label="Название") # поиск по части слова и без учёта регистра
    
    class Meta:
        model = Genre
        fields = ("name",)
