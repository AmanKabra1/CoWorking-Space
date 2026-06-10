from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from apps.core.exporters import build_export_response
from .models import Vendor, VendorBill
from .serializers import VendorSerializer, VendorBillSerializer


def _leased_building_ids(user):
    """Building IDs the user's company occupies (via desks or parking)."""
    from apps.workspace.models import Desk, ParkingSlot
    if not user.company_id:
        return []
    desk_ids = Desk.objects.filter(
        company_id=user.company_id
    ).values_list('room__floor__building_id', flat=True)
    park_ids = ParkingSlot.objects.filter(
        company_id=user.company_id
    ).values_list('building_id', flat=True)
    return list(set(desk_ids) | set(park_ids))


@extend_schema_view(
    list=extend_schema(tags=['Vendors']),
    retrieve=extend_schema(tags=['Vendors']),
    create=extend_schema(tags=['Vendors']),
    update=extend_schema(tags=['Vendors']),
    partial_update=extend_schema(tags=['Vendors']),
    destroy=extend_schema(tags=['Vendors']),
)
class VendorViewSet(viewsets.ModelViewSet):
    """Vendors / suppliers. Super Admin: all. Company Admin: own buildings + operator-wide."""

    serializer_class = VendorSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['category', 'building', 'is_active']
    search_fields = ['name', 'contact_person', 'gst_number']

    def get_queryset(self):
        user = self.request.user
        qs = Vendor.objects.select_related('building')
        if user.is_super_admin:
            return qs
        building_ids = _leased_building_ids(user)
        return qs.filter(building_id__in=building_ids) | qs.filter(building__isnull=True)


@extend_schema_view(
    list=extend_schema(tags=['Vendors']),
    retrieve=extend_schema(tags=['Vendors']),
    create=extend_schema(tags=['Vendors']),
    update=extend_schema(tags=['Vendors']),
    partial_update=extend_schema(tags=['Vendors']),
    destroy=extend_schema(tags=['Vendors']),
)
class VendorBillViewSet(viewsets.ModelViewSet):
    """Vendor bills / expenses. Scoped to building like vendors."""

    serializer_class = VendorBillSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['vendor', 'building', 'status']
    search_fields = ['bill_number', 'description']

    def get_queryset(self):
        user = self.request.user
        qs = VendorBill.objects.select_related('vendor', 'building')
        if user.is_super_admin:
            return qs
        return qs.filter(building_id__in=_leased_building_ids(user))

    @extend_schema(tags=['Vendors'], responses={200: VendorBillSerializer})
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """Mark a bill as paid."""
        bill = self.get_object()
        bill.status = VendorBill.PAID
        bill.paid_at = timezone.now()
        bill.save(update_fields=['status', 'paid_at', 'updated_at'])
        return Response(VendorBillSerializer(bill).data)

    @extend_schema(tags=['Vendors'])
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Download vendor bills as Excel / Word / PDF (?format=excel|word|pdf)."""
        bills = self.filter_queryset(self.get_queryset())
        headers = ['Bill #', 'Vendor', 'Building', 'Bill Date', 'Due Date', 'Amount', 'Tax', 'Total', 'Status']
        rows = [
            [
                b.bill_number, b.vendor.name, b.building.name,
                b.bill_date, b.due_date or '', b.amount, b.tax_amount,
                b.total_amount, b.get_status_display(),
            ]
            for b in bills
        ]
        return build_export_response(
            request.query_params.get('fmt'),
            'vendor_bills', 'CoWorkHub — Vendor Bills', headers, rows,
        )

    @extend_schema(tags=['Vendors'])
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """Totals by status across the visible bills."""
        qs = self.get_queryset()
        totals = {
            'total_bills': qs.count(),
            'total_amount': qs.aggregate(s=Sum('total_amount'))['s'] or 0,
            'pending_amount': qs.filter(status=VendorBill.PENDING).aggregate(s=Sum('total_amount'))['s'] or 0,
            'paid_amount': qs.filter(status=VendorBill.PAID).aggregate(s=Sum('total_amount'))['s'] or 0,
            'overdue_amount': qs.filter(status=VendorBill.OVERDUE).aggregate(s=Sum('total_amount'))['s'] or 0,
        }
        return Response(totals)
