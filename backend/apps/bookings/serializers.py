from decimal import Decimal
from datetime import datetime
from rest_framework import serializers
from django.utils import timezone
from .models import Booking
from apps.companies.models import Company


def _compute_booking_financials(facility, start_time, end_time):
    start = datetime.combine(datetime.min.date(), start_time)
    end = datetime.combine(datetime.min.date(), end_time)
    duration = Decimal(str(round((end - start).total_seconds() / 3600, 2)))
    if duration >= 8:
        amount = facility.price_per_day
    else:
        amount = (facility.price_per_hour * duration).quantize(Decimal('0.01'))
    return duration, amount


class BookingListSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    facility_type = serializers.CharField(source='facility.facility_type', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    booked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'facility', 'facility_name', 'facility_type',
            'company', 'company_name', 'booked_by', 'booked_by_name',
            'booking_date', 'start_time', 'end_time', 'duration_hours',
            'status', 'purpose', 'attendees_count', 'total_amount',
            'created_at',
        ]

    def get_booked_by_name(self, obj):
        return obj.booked_by.get_full_name()


class BookingSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    facility_type = serializers.CharField(source='facility.facility_type', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    booked_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'facility', 'facility_name', 'facility_type',
            'company', 'company_name', 'booked_by', 'booked_by_name',
            'booking_date', 'start_time', 'end_time', 'duration_hours',
            'status', 'purpose', 'attendees_count', 'total_amount',
            'approved_by', 'approved_by_name', 'approved_at',
            'rejection_reason', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'company', 'booked_by', 'duration_hours', 'total_amount',
            'approved_by', 'approved_at', 'status', 'created_at', 'updated_at',
        ]

    def get_booked_by_name(self, obj):
        return obj.booked_by.get_full_name()

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None


class CreateBookingSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(status=Company.ACTIVE),
        required=False,
        help_text='Required only for Super Admin. Auto-set for Company Admin/Employee.',
    )

    class Meta:
        model = Booking
        fields = [
            'facility', 'company',
            'booking_date', 'start_time', 'end_time',
            'purpose', 'attendees_count',
        ]

    def validate(self, attrs):
        request = self.context['request']
        facility = attrs['facility']
        booking_date = attrs['booking_date']
        start_time = attrs['start_time']
        end_time = attrs['end_time']
        attendees = attrs.get('attendees_count', 1)

        if not facility.is_active:
            raise serializers.ValidationError({'facility': 'This facility is currently inactive.'})

        if end_time <= start_time:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})

        if booking_date < timezone.localdate():
            raise serializers.ValidationError({'booking_date': 'Booking date cannot be in the past.'})

        if attendees > facility.capacity:
            raise serializers.ValidationError({
                'attendees_count': f'Exceeds facility capacity of {facility.capacity} people.'
            })

        # Overlap check — exclude cancelled/rejected
        conflict = Booking.objects.filter(
            facility=facility,
            booking_date=booking_date,
            status__in=[Booking.PENDING, Booking.APPROVED],
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if self.instance:
            conflict = conflict.exclude(pk=self.instance.pk)
        if conflict.exists():
            raise serializers.ValidationError({
                'start_time': 'This time slot conflicts with an existing booking.'
            })

        # Company assignment
        if not request.user.is_super_admin:
            if not request.user.company:
                raise serializers.ValidationError(
                    {'detail': 'Your account is not linked to a company.'}
                )
            attrs['company'] = request.user.company
        else:
            if 'company' not in attrs:
                raise serializers.ValidationError(
                    {'company': 'Company is required for Super Admin bookings.'}
                )

        return attrs

    def create(self, validated_data):
        facility = validated_data['facility']
        duration, amount = _compute_booking_financials(
            facility,
            validated_data['start_time'],
            validated_data['end_time'],
        )
        return Booking.objects.create(
            **validated_data,
            duration_hours=duration,
            total_amount=amount,
        )


class RejectBookingSerializer(serializers.Serializer):
    reason = serializers.CharField(
        required=False, allow_blank=True,
        help_text='Optional reason shown to the company.',
    )


class CalendarBookingSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    facility_type = serializers.CharField(source='facility.facility_type', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'facility', 'facility_name', 'facility_type',
            'company', 'company_name',
            'booking_date', 'start_time', 'end_time', 'duration_hours',
            'status', 'total_amount',
        ]
