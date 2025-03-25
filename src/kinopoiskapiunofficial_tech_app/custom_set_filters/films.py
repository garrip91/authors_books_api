from django.db.models import functions
from django_filters import rest_framework as filters, DateTimeFilter

from ..models import Film


class FilmFilterSet(filters.FilterSet):
    """Класс для фильтрации фильмов по критериям"""

    kinopoisk_id = filters.CharFilter(lookup_expr="icontains", label="ID на сайте")
    name = filters.CharFilter(lookup_expr="icontains", label="Название") # поиск по части слова и без учёта регистра
    actors = filters.CharFilter(field_name="actors__name", lookup_expr="icontains", label="Актёры")
    
    # ФИЛЬТРАЦИЯ ПО ГОДАМ ВЫХОДА:
    year_gte = filters.NumberFilter(field_name="year", lookup_expr="gte", label="Год выхода (от)")  # поиск по году выхода по критерию ">="
    year_lte = filters.NumberFilter(field_name="year", lookup_expr="lte", label="Год выхода (до)")  # поиск по году выхода по критерию "<="

    created_or_updated_at_gte = DateTimeFilter(
        field_name="updated_at",
        lookup_expr="gte",
        label="Создано/Обновлено на стороне нашего проекта (от) (ДД.ММ.ГГГГ)",
        input_formats=("%d.%m.%Y",)
    )

    created_or_updated_at_lte = DateTimeFilter(
        field_name="updated_at",
        lookup_expr="lte",
        label="Создано/Обновлено на стороне нашего проекта (до) (ДД.ММ.ГГГГ)",
        input_formats=("%d.%m.%Y",)
    )

    class Meta:
        model = Film
        fields = ("kinopoisk_id", "name", "actors",)
