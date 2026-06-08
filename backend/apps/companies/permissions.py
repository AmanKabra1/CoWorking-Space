from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.models import User


class CanViewOwnCompany(BasePermission):
    """
    Super Admins: full access to all companies.
    Company Admins / Employees: read-only access to their own company only.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin:
            return True
        # Company admin or employee: must belong to the company, read-only
        if request.user.company_id == obj.id:
            return request.method in SAFE_METHODS
        return False
