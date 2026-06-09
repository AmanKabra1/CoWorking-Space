from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Booking
from .serializers import (
    BookingSerializer, BookingListSerializer,
    CreateBookingSerializer, RejectBookingSerializer,
    CalendarBookingSerializer,
)
from .permissions import CanCreateBooking, CanApproveBooking
from apps.core.exporters import build_export_response


@extend_schema_view(
    list=extend_schema(tags=['Bookings']),
    retrieve=extend_schema(tags=['Bookings']),
    create=extend_schema(tags=['Bookings']),
    update=extend_schema(tags=['Bookings']),
    partial_update=extend_schema(tags=['Bookings']),
    destroy=extend_schema(tags=['Bookings']),
)
class BookingViewSet(viewsets.ModelViewSet):
    """
    Facility booking with full approval workflow.

    Flow: pending → approved / rejected → (completed / cancelled)

    - Create: any authenticated user linked to a company
    - Approve / Reject / Complete: Super Admin only
    - Cancel: booking owner's company admin or Super Admin
    """
    filterset_fields = ['status', 'facility', 'company', 'booking_date']
    search_fields = ['purpose', 'facility__name', 'company__name']

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related(
            'facility', 'company', 'booked_by', 'approved_by'
        )
        if user.is_super_admin:
            return qs
        if user.company_id:
            return qs.filter(company_id=user.company_id)
        return Booking.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateBookingSerializer
        if self.action == 'list':
            return BookingListSerializer
        if self.action == 'calendar':
            return CalendarBookingSerializer
        return BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [CanCreateBooking()]
        if self.action in ['approve', 'reject', 'complete']:
            return [CanApproveBooking()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = self.perform_create(serializer)
        return Response(
            BookingSerializer(booking, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_super_admin:
            return serializer.save(booked_by=user)
        return serializer.save(booked_by=user, company=user.company)

    # ─── Approval workflow actions ─────────────────────────

    @extend_schema(tags=['Bookings'], responses={200: BookingSerializer})
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a pending booking.
        External booking → Super Admin. Internal booking → the company's Company Admin (or Super Admin).
        """
        booking = self.get_object()
        if booking.status != Booking.PENDING:
            return Response(
                {'detail': f'Only pending bookings can be approved. Current status: {booking.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = Booking.APPROVED
        booking.approved_by = request.user
        booking.approved_at = timezone.now()
        booking.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    @extend_schema(tags=['Bookings'], request=RejectBookingSerializer, responses={200: BookingSerializer})
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject a pending booking with an optional reason.
        External booking → Super Admin. Internal booking → the company's Company Admin (or Super Admin).
        """
        booking = self.get_object()
        if booking.status != Booking.PENDING:
            return Response(
                {'detail': f'Only pending bookings can be rejected. Current status: {booking.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RejectBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking.status = Booking.REJECTED
        booking.rejection_reason = serializer.validated_data.get('reason', '')
        booking.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    @extend_schema(tags=['Bookings'], responses={200: BookingSerializer})
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel a booking. Company Admin (own company) or Super Admin."""
        booking = self.get_object()
        if booking.status in [Booking.CANCELLED, Booking.COMPLETED, Booking.REJECTED]:
            return Response(
                {'detail': f'Cannot cancel a booking with status "{booking.status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_super_admin:
            if not request.user.is_company_admin:
                return Response(
                    {'detail': 'Only Company Admin or Super Admin can cancel bookings.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
        booking.status = Booking.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    @extend_schema(tags=['Bookings'], responses={200: BookingSerializer})
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Mark an approved booking as completed.
        External booking → Super Admin. Internal booking → the company's Company Admin (or Super Admin).
        """
        booking = self.get_object()
        if booking.status != Booking.APPROVED:
            return Response(
                {'detail': 'Only approved bookings can be marked as completed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = Booking.COMPLETED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    # ─── List actions ──────────────────────────────────────

    @extend_schema(tags=['Bookings'], responses={200: BookingListSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='pending-queue')
    def pending_queue(self, request):
        """
        Pending bookings awaiting *your* approval, oldest first.
        Super Admin → all pending. Company Admin → own company's internal pending.
        Employees → none.
        """
        user = request.user
        qs = (
            Booking.objects
            .filter(status=Booking.PENDING)
            .select_related('facility', 'company', 'booked_by')
            .order_by('booking_date', 'start_time')
        )
        if not user.is_super_admin:
            if user.is_company_admin and user.company_id:
                qs = qs.filter(booking_type=Booking.INTERNAL, company_id=user.company_id)
            else:
                qs = Booking.objects.none()
        serializer = BookingListSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Bookings'], responses={200: CalendarBookingSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        """
        Bookings within a date range — calendar view.
        Query params: start=YYYY-MM-DD, end=YYYY-MM-DD, facility=UUID (optional)
        """
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if not start or not end:
            return Response(
                {'detail': 'start and end query params are required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self.get_queryset().filter(
            booking_date__gte=start,
            booking_date__lte=end,
        )

        facility_id = request.query_params.get('facility')
        if facility_id:
            qs = qs.filter(facility_id=facility_id)

        # Exclude cancelled/rejected from calendar view by default
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        else:
            qs = qs.exclude(status__in=[Booking.CANCELLED, Booking.REJECTED])

        serializer = CalendarBookingSerializer(qs.order_by('booking_date', 'start_time'), many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Bookings'])
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Download the visible bookings as Excel / Word / PDF (?format=excel|word|pdf)."""
        bookings = self.filter_queryset(self.get_queryset())
        headers = [
            'Facility', 'Company', 'Booked By', 'Date', 'Start', 'End',
            'Type', 'Payment', 'Amount', 'Status',
        ]
        rows = [
            [
                b.facility.name, b.company.name, b.booked_by.get_full_name(),
                b.booking_date, b.start_time, b.end_time,
                b.get_booking_type_display(),
                'Required' if b.payment_required else 'Free',
                b.total_amount, b.get_status_display(),
            ]
            for b in bookings
        ]
        return build_export_response(
            request.query_params.get('format'),
            'bookings', 'CoWorkHub — Bookings', headers, rows,
        )
