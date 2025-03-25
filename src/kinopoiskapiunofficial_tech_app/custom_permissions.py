from rest_framework import permissions


class ReadForAllCreateUpdateDeleteForOwnerOrAdmin(permissions.BasePermission):
    """
    Кастомный класс, предоставляющий следующие права доступа к записям из БД:
        -> Create (создание) - только конкретным аутентифицированным пользователям, а именно: владельцам записей и админам проекта
        -> Read (чтение) - всем аутентифицированным пользователям
        -> Update (изменение) - только конкретным аутентифицированным пользователям, а именно: владельцам записей и админам проекта
        -> Delete (удаление) - только конкретным аутентифицированным пользователям, а именно: владельцам записей и админам проекта

    """
    
    def has_permission(self, request, view):
        # ОПРЕАЦИЯ ЧТЕНИЯ ДОСТУПНА ВСЕМ АУТЕНТИФИЦИРОВАННЫМ ПОЛЬЗОВАТЕЛЯМ:
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        # ОПЕРАЦИИ СОЗДАНИЯ, ИЗМЕНЕНИЯ И УДАЛЕНИЯ ДОСТУПНЫ ТОЛЬКО ВЛАДЕЛЬЦАМ ЗАПИСЕЙ И АДМИНАМ ПРОЕКТА:
        return bool(request.user and (request.user.is_owner or request.user.is_staff))
    
    def has_object_permission(self, request, view, obj):
        # ОПРЕАЦИЯ ЧТЕНИЯ ДОСТУПНА ВСЕМ АУТЕНТИФИЦИРОВАННЫМ ПОЛЬЗОВАТЕЛЯМ:
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        # ОПЕРАЦИИ СОЗДАНИЯ, ИЗМЕНЕНИЯ И УДАЛЕНИЯ ДОСТУПНЫ ТОЛЬКО ВЛАДЕЛЬЦАМ ЗАПИСЕЙ И АДМИНАМ ПРОЕКТА:
        return bool(request.user and (request.user.is_owner or request.user.is_staff))
