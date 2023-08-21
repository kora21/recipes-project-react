from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только для автора.
    Остальным только чтение объекта."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение только для администратора.
    Остальным только чтение объекта."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)
