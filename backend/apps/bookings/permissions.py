from rest_framework.permissions import BasePermission


class CanCreateBooking(BasePermission):
    """Any authenticated user linked to a company can request a booking."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_super_admin:
            return True
        return request.user.company_id is not None
