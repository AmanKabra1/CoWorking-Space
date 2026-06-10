from rest_framework import serializers

from apps.facilities.models import Facility


class PublicFacilitySerializer(serializers.ModelSerializer):
    """Minimal, safe facility fields exposed to anonymous visitors."""

    facility_type_display = serializers.CharField(source='get_facility_type_display', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Facility
        fields = [
            'id', 'name', 'facility_type', 'facility_type_display',
            'building_name', 'capacity', 'price_per_hour', 'price_per_day',
            'description', 'amenities',
        ]
