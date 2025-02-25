from django.db.models import functions
from django_filters import rest_framework as filters

from ..models import Author


class AuthorFilterSet(filters.FilterSet):
    """Класс для фильтрации авторов по критериям"""

    first_name = filters.CharFilter(lookup_expr="icontains") # поиск по части слова и без учёта регистра
    last_name = filters.CharFilter(lookup_expr="icontains") # поиск по части слова и без учёта регистра
    
    # ФИЛЬТРАЦИЯ ПО ГОДАМ РОЖДЕНИЯ:
    birth_year_gte = filters.NumberFilter(method="filter_birth_year_gte", label="Год рождения (от)") # поиск по году рождения по критерию ">="
    birth_year_lte = filters.NumberFilter(method="filter_birth_year_lte", label="Год рождения (до)") # поиск по году рождения по критерию "<="

    # ФИЛЬТРАЦИЯ ПО ГОДАМ СМЕРТИ:
    death_year_gte = filters.NumberFilter(method="filter_death_year_gte", label="Год смерти (от)") # поиск по году смерти по критерию ">="
    death_year_lte = filters.NumberFilter(method="filter_death_year_lte", label="Год смерти (до)") # поиск по году смерти по критерию "<="

    def filter_birth_year_gte(self, queryset, name, value):
        """Фильтрация по годам рождения (>=)"""
        return queryset.annotate(birth_year=functions.ExtractYear("date_of_birth")).filter(
            birth_year__gte=value
        )
    
    def filter_birth_year_lte(self, queryset, name, value):
        """Фильтрация по годам рождения (<=)"""
        return queryset.annotate(birth_year=functions.ExtractYear("date_of_birth")).filter(
            birth_year__lte=value
        )

    def filter_death_year_gte(self, queryset, name, value):
        """Фильтрация по годам смерти (>=)"""
        return queryset.annotate(death_year=functions.ExtractYear("date_of_death")).filter(
            death_year__gte=value
        )

    def filter_death_year_lte(self, queryset, name, value):
        """Фильтрация по годам смерти (<=)"""
        return queryset.annotate(death_year=functions.ExtractYear("date_of_death")).filter(
            death_year__lte=value
        )
    
    class Meta:
        model = Author
        fields = ["first_name", "last_name"]
