from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from apps.workspace.models import Desk
from .models import SeatLease
from .serializers import SeatLeaseSerializer


@extend_schema_view(
    list=extend_schema(tags=['Subleasing']),
    retrieve=extend_schema(tags=['Subleasing']),
    create=extend_schema(tags=['Subleasing']),
    update=extend_schema(tags=['Subleasing']),
    partial_update=extend_schema(tags=['Subleasing']),
    destroy=extend_schema(tags=['Subleasing']),
)
class SeatLeaseViewSet(viewsets.ModelViewSet):
    """
    Sub-leases of a company's assigned desks.
    Super Admin: all. Company Admin: only their own company's sub-leases.
    """

    serializer_class = SeatLeaseSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['status', 'desk', 'lessor_company']
    search_fields = ['lessee_name', 'lessee_company', 'desk__desk_code']

    def get_queryset(self):
        user = self.request.user
        qs = SeatLease.objects.select_related('desk', 'desk__room', 'lessor_company')
        if user.is_super_admin:
            return qs
        return qs.filter(lessor_company_id=user.company_id)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_super_admin:
            # Super admin sub-leases on behalf of the desk's owning company.
            desk = serializer.validated_data['desk']
            serializer.save(lessor_company_id=desk.company_id)
        else:
            serializer.save(lessor_company_id=user.company_id)

    @extend_schema(tags=['Subleasing'], responses={200: SeatLeaseSerializer})
    @action(detail=True, methods=['post'], url_path='end')
    def end(self, request, pk=None):
        """End an active sub-lease (sets status=ended and end_date=today)."""
        lease = self.get_object()
        if lease.status != SeatLease.ACTIVE:
            return Response({'detail': 'Only active sub-leases can be ended.'},
                            status=status.HTTP_400_BAD_REQUEST)
        lease.status = SeatLease.ENDED
        if not lease.end_date:
            lease.end_date = timezone.localdate()
        lease.save(update_fields=['status', 'end_date', 'updated_at'])
        return Response(SeatLeaseSerializer(lease, context={'request': request}).data)

    @extend_schema(tags=['Subleasing'])
    @action(detail=False, methods=['get'], url_path='available-desks')
    def available_desks(self, request):
        """Desks the user can sub-lease (assigned to their company, no active sub-lease)."""
        user = request.user
        desks = Desk.objects.select_related('room', 'room__floor', 'room__floor__building')
        if user.is_super_admin:
            desks = desks.filter(company__isnull=False)
        else:
            desks = desks.filter(company_id=user.company_id)

        leased_ids = set(
            SeatLease.objects.filter(status=SeatLease.ACTIVE).values_list('desk_id', flat=True)
        )
        data = [
            {
                'id': str(d.id),
                'desk_code': d.desk_code,
                'location': str(d.room),
                'monthly_rate': str(d.monthly_rate),
            }
            for d in desks if d.id not in leased_ids
        ]
        return Response(data)
