from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from apps.accounts.models import User
from apps.notifications.email import send_email
from .models import SeatListing, SeatApplication
from .listing_serializers import SeatListingSerializer, SeatApplicationSerializer


@extend_schema_view(
    list=extend_schema(tags=['Subleasing']),
    create=extend_schema(tags=['Subleasing']),
    retrieve=extend_schema(tags=['Subleasing']),
    update=extend_schema(tags=['Subleasing']),
    partial_update=extend_schema(tags=['Subleasing']),
    destroy=extend_schema(tags=['Subleasing']),
)
class SeatListingViewSet(viewsets.ModelViewSet):
    """Startup seat listings. Company admin manages own; super admin sees all."""

    serializer_class = SeatListingSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['is_open', 'building', 'lessor_company']

    def get_queryset(self):
        user = self.request.user
        qs = SeatListing.objects.select_related('lessor_company', 'building', 'floor')
        if user.is_super_admin:
            return qs
        return qs.filter(lessor_company_id=user.company_id)

    def perform_create(self, serializer):
        serializer.save(lessor_company_id=self.request.user.company_id)


@extend_schema_view(
    list=extend_schema(tags=['Subleasing']),
    create=extend_schema(tags=['Subleasing']),
    retrieve=extend_schema(tags=['Subleasing']),
)
class SeatApplicationViewSet(viewsets.ModelViewSet):
    """
    Applications to seat listings. Anyone authenticated can apply (a startup).
    The listing's company admin approves/rejects; super admin is notified on approval.
    """

    serializer_class = SeatApplicationSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = SeatApplication.objects.select_related('listing', 'listing__lessor_company')
        if user.is_super_admin:
            return qs
        if user.is_company_admin:
            return qs.filter(listing__lessor_company_id=user.company_id)
        # applicants see their own (by email match is unreliable) — none for employees
        return SeatApplication.objects.none()

    def _can_review(self, application, user):
        return user.is_super_admin or (
            user.is_company_admin and application.listing.lessor_company_id == user.company_id
        )

    @extend_schema(tags=['Subleasing'])
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        application = self.get_object()
        if not self._can_review(application, request.user):
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        if application.status != SeatApplication.PENDING:
            return Response({'detail': 'Already reviewed.'}, status=status.HTTP_400_BAD_REQUEST)
        application.status = SeatApplication.APPROVED
        application.reviewed_at = timezone.now()
        application.save(update_fields=['status', 'reviewed_at', 'updated_at'])
        _notify_super_admins(application)
        return Response(SeatApplicationSerializer(application).data)

    @extend_schema(tags=['Subleasing'])
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        application = self.get_object()
        if not self._can_review(application, request.user):
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        if application.status != SeatApplication.PENDING:
            return Response({'detail': 'Already reviewed.'}, status=status.HTTP_400_BAD_REQUEST)
        application.status = SeatApplication.REJECTED
        application.reviewed_at = timezone.now()
        application.save(update_fields=['status', 'reviewed_at', 'updated_at'])
        return Response(SeatApplicationSerializer(application).data)


def _notify_super_admins(application):
    """Super admin gets visibility only — no approval needed (company already paid)."""
    listing = application.listing
    subject = f'Seat sub-lease approved — {listing.lessor_company.name}'
    body = (
        f"{listing.lessor_company.name} approved a startup for spare seats (FYI — no action needed).\n\n"
        f"Listing: {listing.title}\n"
        f"Startup: {application.startup_name} ({application.contact_email})\n"
        f"Seats: {application.seats_requested}\n"
        f"Building: {listing.building.name}\n"
    )
    emails = User.objects.filter(role=User.SUPER_ADMIN, is_active=True).exclude(email='').values_list('email', flat=True)
    for email in emails:
        send_email(email, subject, body)
