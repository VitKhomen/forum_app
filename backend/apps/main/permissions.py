from rest_framework import permissions


class IsAuthorOrStaff(permissions.BasePermission):
    """
    Дозволяє:
    - автору поста
    - staff / superuser
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS (GET, HEAD, OPTIONS) — можна всім
        if request.method in permissions.SAFE_METHODS:
            return True

        # Staff і superuser можуть все
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True

        # Автор поста
        return obj.author == request.user
