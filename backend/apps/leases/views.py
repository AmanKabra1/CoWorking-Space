from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Lease
from .serializers import LeaseSerializer


class IsSuperAdminOrReadOnly(BasePermission):
    """Read: any authenticated user (scoped in queryset). Write: Super Admin only."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_super_admin


@extend_schema_view(
    list=extend_schema(tags=['Leases']),
    retrieve=extend_schema(tags=['Leases']),
    create=extend_schema(tags=['Leases']),
    update=extend_schema(tags=['Leases']),
    partial_update=extend_schema(tags=['Leases']),
    destroy=extend_schema(tags=['Leases']),
)
class LeaseViewSet(viewsets.ModelViewSet):
    """
    Lease agreements. Super Admin: full CRUD on all.
    Company Admin / employees: read-only, their own company's leases.
    """

    serializer_class = LeaseSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    filterset_fields = ['status', 'company', 'building']
    search_fields = ['company__name', 'building__name']

    def get_queryset(self):
        user = self.request.user
        qs = Lease.objects.select_related('company', 'building', 'floor')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company_id=user.company_id)
        return Lease.objects.none()
