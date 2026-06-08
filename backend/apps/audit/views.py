from rest_framework import viewsets

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['action', 'resource_type']
    search_fields = ['description', 'user__email']
    ordering_fields = ['created_at', 'action']

    def get_queryset(self):
        user = self.request.user
        qs = AuditLog.objects.select_related('user', 'company')
        if user.is_super_admin:
            return qs
        return qs.filter(company=user.company)
