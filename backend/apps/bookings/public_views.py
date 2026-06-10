"""
Public (no-login) booking endpoints.

External visitors can list facilities that are open to the public, check a
facility's availability for a date, and submit a booking request. Requests
are created as pending external bookings for a super admin to approve.
"""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.facilities.models import Facility
from .models import Booking
from .serializers import PublicBookingSerializer
from .public_serializers import PublicFacilitySerializer


@extend_schema(tags=['Public'])
class PublicFacilityListView(generics.ListAPIView):
    """Facilities open for public booking. No auth required."""

    permission_classes = [AllowAny]
    serializer_class = PublicFacilitySerializer

    def get_queryset(self):
        return Facility.objects.filter(is_active=True, is_public=True).select_related('building')


@extend_schema(tags=['Public'])
class PublicAvailabilityView(APIView):
    """Booked time slots for a public facility on a date, so the UI can hide them."""

    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        date = request.query_params.get('date')
        if not date:
            return Response({'detail': 'date query param is required (YYYY-MM-DD).'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            facility = Facility.objects.get(pk=pk, is_active=True, is_public=True)
        except Facility.DoesNotExist:
            return Response({'detail': 'Facility not found.'}, status=status.HTTP_404_NOT_FOUND)

        slots = (
            Booking.objects
            .filter(facility=facility, booking_date=date,
                    status__in=[Booking.PENDING, Booking.APPROVED])
            .values('start_time', 'end_time')
            .order_by('start_time')
        )
        return Response({'booked_slots': [
            {'start': s['start_time'].strftime('%H:%M'), 'end': s['end_time'].strftime('%H:%M')}
            for s in slots
        ]})


@extend_schema(tags=['Public'], request=PublicBookingSerializer, responses={201: PublicBookingSerializer})
class PublicBookingCreateView(generics.CreateAPIView):
    """Submit a guest booking request (pending super-admin approval). No auth."""

    permission_classes = [AllowAny]
    serializer_class = PublicBookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(
            {
                'id': str(booking.id),
                'status': booking.status,
                'total_amount': str(booking.total_amount),
                'detail': 'Booking request received. You will get an email once it is reviewed.',
            },
            status=status.HTTP_201_CREATED,
        )
