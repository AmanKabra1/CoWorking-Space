from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperAdmin(BasePermission):
    """Only Super Admins."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_super_admin
        )


class IsCompanyAdmin(BasePermission):
    """Only Company Admins."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_company_admin
        )


class IsSuperAdminOrCompanyAdmin(BasePermission):
    """Super Admin or Company Admin."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_super_admin or request.user.is_company_admin)
        )


class IsOwnerOrSuperAdmin(BasePermission):
    """Object-level: owner of the record or Super Admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin:
            return True
        return obj == request.user
