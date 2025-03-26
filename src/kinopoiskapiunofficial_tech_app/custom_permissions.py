from rest_framework import permissions


class ReadForAllCreateUpdateDeleteForOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомный класс, предоставляющий следующие права доступа к записям из БД:
        -> Create (создание) - только аутентифицированным пользователям
        -> Read (чтение) - всем пользователям
        -> Update (изменение) - только конкретным аутентифицированным пользователям, а именно: владельцам записей и админам проекта
        -> Delete (удаление) - только конкретным аутентифицированным пользователям, а именно: владельцам записей и админам проекта

    """
    
    def has_permission(self, request, view):
        # ДЛЯ БЕЗОПАСНЫХ МЕТОДОВ ("GET", "HEAD" И "OPTIONS"), А ИМЕННО - ДЛЯ СОВЕРШЕНИЯ ОПЕРАЦИИ ЧТЕНИЯ, РАЗРЕШАЕМ ДОСТУП ВСЕМ:
        if request.method in permissions.SAFE_METHODS:
            return True
        # ДЛЯ СОЗДАНИЯ ЗАПИСЕЙ (МЕТОД "POST") РАЗРЕШАЕМ ДОСТУП ТОЛЬКО АУТЕНТИФИЦИРОВАННЫМ ПОЛЬЗОВАТЕЛЯМ:
        if request.method == "POST":
            return request.user.is_authenticated
        # ДЛЯ ОСТАЛЬНЫХ НЕБЕЗОПАСНЫХ МЕТОДОВ ("UPDATE", "PUT", "PATCH" И "DELETE") РАЗРЕШАЕМ ДОСТУПЫ ТОЛЬКО ВЛАДЕЛЬЦАМ ЗАПИСЕЙ И АДМИНАМ ПРОЕКТА:
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # ОПЕРАЦИЮ "READ" РАЗРЕШАЕМ ВСЕМ:
        if request.method in permissions.SAFE_METHODS:
            return True
        # ОПЕРАЦИИ "UPDATE" И "DELETE" РАЗРЕШАЕМ ТОЛЬКО ВЛАДЕЛЬЦАМ ЗАПИСЕЙ И АДМИНАМ ПРОЕКТА:
        return obj.owner == request.user or request.user.is_staff
