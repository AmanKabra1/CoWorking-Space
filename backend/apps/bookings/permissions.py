from rest_framework.permissions import BasePermission

from .models import Booking


class CanCreateBooking(BasePermission):
    """Any authenticated user linked to a company can request a booking."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_super_admin:
            return True
        return request.user.company_id is not None


class CanApproveBooking(BasePermission):
    """
    Who may approve / reject / complete a booking:
      - External booking  → Super Admin only (paid booking by an outside company)
      - Internal booking  → Company Admin of the booking's own company, or Super Admin
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_super_admin:
            return True
        if (
            obj.booking_type == Booking.INTERNAL
            and user.is_company_admin
            and obj.company_id == user.company_id
        ):
            return True
        return False
