from rest_framework import permissions


# КЛАСС, ОПРЕДЕЛЯЮЩИЙ ИМЕЕТ ЛИ ПОЛЬЗОВАТЕЛЬ ПРАВО НА ВЫПОЛНЕНИЕ ОПРЕДЕЛЁННЫХ ДЕЙСТВИЙ (изменение, удаление и так далее...):
class IsOwnerOrReadOnly(permissions.BasePermission):
    """Кастомный класс, определяющий права доступа для пользователей (для его использования необходимо в "views.ModelViewSet" добавить `permission_classes = [IsOwnerOrReadOnly])`"""
    
    # ВЫЗЫВАЕМ МЕТОД ОТ DRF ДЛЯ ПРОВЕРКИ ПРАВ ДОСТУПА К КОНКРЕТНОМУ ОБЪЕКТУ (в нашем случае к записям из БД):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # `SAFE_METHODS` - это HTTP-методы, которые считаются "безопасными" (только для чтения)
            return True # разрешаем доступ в случае, если метод из нашего входящего в функцию запроса "безопасный"
        return obj.owner == request.user # возвращаем `True`, если текущий пользователь является владельцем объекта и `False`, если не является
