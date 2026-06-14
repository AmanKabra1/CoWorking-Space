from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Facility, FacilityImage
from .serializers import (
    FacilitySerializer, FacilityListSerializer,
    FacilityImageSerializer, AddFacilityImageSerializer,
)
from .permissions import IsFacilityAdminOrReadOnly
from apps.accounts.permissions import IsSuperAdmin


@extend_schema_view(
    list=extend_schema(tags=['Facilities']),
    retrieve=extend_schema(tags=['Facilities']),
    create=extend_schema(tags=['Facilities']),
    update=extend_schema(tags=['Facilities']),
    partial_update=extend_schema(tags=['Facilities']),
    destroy=extend_schema(tags=['Facilities']),
)
class FacilityViewSet(viewsets.ModelViewSet):
    """
    Manage bookable facilities (conference rooms, studios, event halls, etc.).
    Super Admin: full CRUD. Others: read-only.
    """
    permission_classes = [IsFacilityAdminOrReadOnly]
    filterset_fields = ['facility_type', 'building', 'floor', 'is_active']
    search_fields = ['name', 'description']

    def get_queryset(self):
        return Facility.objects.select_related('building', 'floor', 'owner_company').prefetch_related('images')

    def get_serializer_class(self):
        return FacilityListSerializer if self.action == 'list' else FacilitySerializer

    def perform_create(self, serializer):
        user = self.request.user
        # Company admins' facilities are owned by their company; super-admin
        # facilities are building-wide (owner_company stays null).
        if user.is_company_admin and not user.is_super_admin:
            serializer.save(owner_company_id=user.company_id)
        else:
            serializer.save()

    @extend_schema(tags=['Facilities'])
    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, pk=None):
        """Recent reviews/comments left for this facility."""
        facility = self.get_object()
        reviews = facility.reviews.order_by('-created_at')[:30]
        return Response([
            {
                'rating': r.rating,
                'comment': r.comment,
                'reviewer_name': r.reviewer_name,
                'company_name': r.company_name,
                'created_at': r.created_at.date().isoformat(),
            }
            for r in reviews
        ])

    # ─── Availability ─────────────────────────────────────

    @extend_schema(tags=['Facilities'])
    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """
        Return booked time slots for a given date.
        Query param: ?date=YYYY-MM-DD (required)
        """
        date = request.query_params.get('date')
        if not date:
            return Response(
                {'detail': 'date query param is required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        facility = self.get_object()
        from apps.bookings.models import Booking

        booked = (
            Booking.objects
            .filter(
                facility=facility,
                booking_date=date,
                status__in=[Booking.PENDING, Booking.APPROVED],
            )
            .values('id', 'start_time', 'end_time', 'status')
            .order_by('start_time')
        )

        return Response({
            'facility_id': str(facility.id),
            'facility_name': facility.name,
            'date': date,
            'booked_slots': [
                {
                    'booking_id': str(b['id']),
                    'start': b['start_time'].strftime('%H:%M'),
                    'end': b['end_time'].strftime('%H:%M'),
                    'status': b['status'],
                }
                for b in booked
            ],
        })

    # ─── Image management ─────────────────────────────────

    @extend_schema(tags=['Facilities'], request=AddFacilityImageSerializer, responses={201: FacilityImageSerializer})
    @action(
        detail=True, methods=['post'], url_path='add-image',
        permission_classes=[IsSuperAdmin],
    )
    def add_image(self, request, pk=None):
        """Upload an image for a facility. Super Admin only."""
        facility = self.get_object()
        serializer = AddFacilityImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_primary = serializer.validated_data.get('is_primary', False)
        if is_primary:
            facility.images.filter(is_primary=True).update(is_primary=False)
        elif not facility.images.exists():
            serializer.validated_data['is_primary'] = True

        image = serializer.save(facility=facility)
        return Response(FacilityImageSerializer(image, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Facilities'])
    @action(
        detail=True, methods=['delete'], url_path=r'images/(?P<image_id>[^/.]+)',
        permission_classes=[IsSuperAdmin],
    )
    def remove_image(self, request, pk=None, image_id=None):
        """Remove a facility image. Super Admin only."""
        facility = self.get_object()
        try:
            image = facility.images.get(id=image_id)
        except FacilityImage.DoesNotExist:
            return Response({'detail': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
