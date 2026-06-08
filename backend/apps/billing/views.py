from datetime import date, timedelta
from decimal import Decimal

from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsSuperAdmin
from .models import Invoice, Payment
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer,
    CreateInvoiceSerializer,
    PaymentSerializer, RecordPaymentSerializer,
)
from .pdf import generate_invoice_pdf


@extend_schema_view(
    list=extend_schema(tags=['Billing']),
    retrieve=extend_schema(tags=['Billing']),
    create=extend_schema(tags=['Billing']),
    update=extend_schema(tags=['Billing']),
    partial_update=extend_schema(tags=['Billing']),
    destroy=extend_schema(tags=['Billing']),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Invoice CRUD + workflow actions.

    - List / retrieve: Super Admin sees all; Company Admin sees own company.
    - Create / update / delete: Super Admin only.
    - send: moves DRAFT → SENT.
    - record_payment: partial or full payment recording.
    - mark_overdue: SENT → OVERDUE.
    - cancel: DRAFT/SENT → CANCELLED.
    - download_pdf: streams the PDF invoice.
    - generate_monthly: auto-generate invoices for all active companies.
    """
    filterset_fields = ['status', 'company', 'billing_period_start', 'billing_period_end']
    search_fields = ['invoice_number', 'company__name']

    def get_queryset(self):
        user = self.request.user
        qs = Invoice.objects.select_related('company').prefetch_related('payments')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company_id=user.company_id)
        return Invoice.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateInvoiceSerializer
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'send', 'mark_overdue', 'cancel', 'generate_monthly',
                           'record_payment']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)

    # ─── Workflow actions ──────────────────────────────────

    @extend_schema(tags=['Billing'], responses={200: InvoiceSerializer})
    @action(detail=True, methods=['post'], url_path='send')
    def send(self, request, pk=None):
        """Move invoice from DRAFT to SENT. Super Admin only."""
        invoice = self.get_object()
        if invoice.status != Invoice.DRAFT:
            return Response(
                {'detail': f'Only draft invoices can be sent. Current status: {invoice.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = Invoice.SENT
        invoice.sent_at = timezone.now()
        invoice.save(update_fields=['status', 'sent_at', 'updated_at'])
        return Response(InvoiceSerializer(invoice).data)

    @extend_schema(tags=['Billing'], request=RecordPaymentSerializer, responses={200: InvoiceSerializer})
    @action(detail=True, methods=['post'], url_path='record-payment', permission_classes=[IsSuperAdmin])
    def record_payment(self, request, pk=None):
        """Record a payment against this invoice. Super Admin only."""
        invoice = self.get_object()
        if invoice.status == Invoice.CANCELLED:
            return Response(
                {'detail': 'Cannot record payment against a cancelled invoice.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecordPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        paid_at = serializer.validated_data.pop('paid_at', None) or timezone.now()
        payment = Payment.objects.create(
            invoice=invoice,
            company=invoice.company,
            recorded_by=request.user,
            status=Payment.COMPLETED,
            paid_at=paid_at,
            **serializer.validated_data,
        )

        # Auto-transition to PAID when fully covered
        total_paid = sum(
            p.amount for p in invoice.payments.filter(status=Payment.COMPLETED)
        )
        if total_paid >= invoice.total_amount and invoice.status != Invoice.PAID:
            invoice.status = Invoice.PAID
            invoice.paid_at = payment.paid_at
            invoice.save(update_fields=['status', 'paid_at', 'updated_at'])

        # Re-fetch with fresh prefetch so amount_paid/amount_due reflect the new payment
        invoice = Invoice.objects.prefetch_related('payments').get(pk=invoice.pk)
        return Response(InvoiceSerializer(invoice).data)

    @extend_schema(tags=['Billing'], responses={200: InvoiceSerializer})
    @action(detail=True, methods=['post'], url_path='mark-overdue')
    def mark_overdue(self, request, pk=None):
        """Mark a SENT invoice as OVERDUE. Super Admin only."""
        invoice = self.get_object()
        if invoice.status != Invoice.SENT:
            return Response(
                {'detail': f'Only sent invoices can be marked overdue. Status: {invoice.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = Invoice.OVERDUE
        invoice.save(update_fields=['status', 'updated_at'])
        return Response(InvoiceSerializer(invoice).data)

    @extend_schema(tags=['Billing'], responses={200: InvoiceSerializer})
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel a DRAFT or SENT invoice. Super Admin only."""
        invoice = self.get_object()
        if invoice.status in [Invoice.PAID, Invoice.CANCELLED]:
            return Response(
                {'detail': f'Cannot cancel a {invoice.status} invoice.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = Invoice.CANCELLED
        invoice.save(update_fields=['status', 'updated_at'])
        return Response(InvoiceSerializer(invoice).data)

    @extend_schema(tags=['Billing'])
    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        """Stream the invoice PDF (generated on-the-fly)."""
        invoice = self.get_object()
        pdf_buffer = generate_invoice_pdf(invoice)
        filename = f"{invoice.invoice_number}.pdf"
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
            content_type='application/pdf',
        )

    @extend_schema(tags=['Billing'])
    @action(detail=False, methods=['post'], url_path='generate-monthly')
    def generate_monthly(self, request):
        """
        Auto-generate draft invoices for all active companies for a billing period.
        Body: {"year": 2026, "month": 7}
        Includes: dedicated desks + parking slots + completed facility bookings.
        Super Admin only.
        """
        year = request.data.get('year')
        month = request.data.get('month')
        if not year or not month:
            return Response(
                {'detail': 'year and month are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            year, month = int(year), int(month)
            period_start = date(year, month, 1)
            if month == 12:
                period_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = date(year, month + 1, 1) - timedelta(days=1)
        except (ValueError, TypeError):
            return Response({'detail': 'Invalid year or month.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.companies.models import Company
        from apps.workspace.models import Desk, ParkingSlot
        from apps.bookings.models import Booking

        companies = Company.objects.filter(status=Company.ACTIVE)
        created_invoices = []

        for company in companies:
            if Invoice.objects.filter(
                company=company,
                billing_period_start=period_start,
                billing_period_end=period_end,
            ).exists():
                continue

            line_items = []
            subtotal = Decimal('0.00')

            # Dedicated desks
            for desk in Desk.objects.filter(company=company, desk_type=Desk.DEDICATED):
                amount = desk.monthly_rate
                line_items.append({
                    'description': f'Desk {desk.desk_code} — Dedicated ({desk.room.name})',
                    'qty': 1, 'rate': str(amount), 'amount': str(amount),
                })
                subtotal += amount

            # Parking slots
            for slot in ParkingSlot.objects.filter(company=company):
                amount = slot.monthly_rate
                line_items.append({
                    'description': f'Parking {slot.slot_number} ({slot.get_slot_type_display()})',
                    'qty': 1, 'rate': str(amount), 'amount': str(amount),
                })
                subtotal += amount

            # Completed facility bookings
            for bk in Booking.objects.filter(
                company=company, status=Booking.COMPLETED,
                booking_date__gte=period_start, booking_date__lte=period_end,
            ).select_related('facility'):
                line_items.append({
                    'description': f'{bk.facility.name} — {bk.booking_date} {bk.start_time}–{bk.end_time}',
                    'qty': 1, 'rate': str(bk.total_amount), 'amount': str(bk.total_amount),
                })
                subtotal += bk.total_amount

            if not line_items:
                continue

            invoice = Invoice(
                company=company,
                invoice_number=Invoice.generate_invoice_number(period_start),
                billing_period_start=period_start,
                billing_period_end=period_end,
                line_items=line_items,
                subtotal=subtotal,
                due_date=period_end + timedelta(days=15),
            )
            invoice.compute_totals()
            invoice.save()
            created_invoices.append(InvoiceListSerializer(invoice).data)

        return Response({
            'generated': len(created_invoices),
            'period': f'{period_start} to {period_end}',
            'invoices': created_invoices,
        })


@extend_schema_view(
    list=extend_schema(tags=['Billing']),
    retrieve=extend_schema(tags=['Billing']),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Payments list/retrieve. Payments are created via InvoiceViewSet.record_payment."""
    serializer_class = PaymentSerializer
    filterset_fields = ['status', 'payment_method', 'invoice', 'company']
    search_fields = ['invoice__invoice_number', 'transaction_id', 'upi_ref']

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('invoice', 'company', 'recorded_by')
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company_id=user.company_id)
        return Payment.objects.none()
