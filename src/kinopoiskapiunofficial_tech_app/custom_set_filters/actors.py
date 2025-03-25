from django.db.models import functions
from django_filters import rest_framework as filters, DateTimeFilter

from ..models import Actor


class ActorFilterSet(filters.FilterSet):
    """Класс для фильтрации актёров по критериям"""
    
    staff_id = filters.CharFilter(lookup_expr="icontains", label="ID актёра на стороне API")
    name = filters.CharFilter(lookup_expr="icontains", label="Имя/Ф.И.О.") # поиск по части слова и без учёта регистра
    poster_url = filters.CharFilter(lookup_expr="icontains", label="Ссылка на постер")
    profession = filters.CharFilter(lookup_expr="icontains", label="Профессия/Специальность")
    created_or_updated_at = filters.CharFilter(lookup_expr="icontains", label="Создано/Обновлено")

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
        model = Actor
        fields = ("staff_id", "name", "poster_url", "profession",)
