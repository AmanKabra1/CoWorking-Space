from rest_framework import serializers
from .models import SeatListing, SeatApplication


class SeatApplicationSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SeatApplication
        fields = [
            'id', 'listing', 'listing_title', 'startup_name', 'contact_email',
            'contact_phone', 'seats_requested', 'message',
            'status', 'status_display', 'reviewed_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'reviewed_at', 'created_at']


class SeatListingSerializer(serializers.ModelSerializer):
    lessor_company_name = serializers.CharField(source='lessor_company.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    application_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()

    class Meta:
        model = SeatListing
        fields = [
            'id', 'lessor_company', 'lessor_company_name', 'building', 'building_name',
            'floor', 'floor_name', 'title', 'seats_available', 'monthly_rate',
            'description', 'is_open', 'application_count', 'pending_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'lessor_company', 'created_at', 'updated_at']

    def get_application_count(self, obj):
        return obj.applications.count()

    def get_pending_count(self, obj):
        return obj.applications.filter(status=SeatApplication.PENDING).count()
