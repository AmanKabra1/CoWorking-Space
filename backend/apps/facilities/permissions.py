from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFacilityAdminOrReadOnly(BasePermission):
    """Super Admin: full CRUD. Authenticated users: read-only."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_super_admin
