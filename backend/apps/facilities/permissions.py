from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFacilityAdminOrReadOnly(BasePermission):
    """
    Read: any authenticated user.
    Write: Super Admin (all facilities) or Company Admin (only facilities their
    company added — owner_company == their company).
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_super_admin or request.user.is_company_admin

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_super_admin:
            return True
        return (
            request.user.is_company_admin
            and obj.owner_company_id is not None
            and obj.owner_company_id == request.user.company_id
        )
