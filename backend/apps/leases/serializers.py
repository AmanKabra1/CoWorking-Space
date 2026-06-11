from rest_framework import serializers
from .models import Lease


class LeaseSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    floor_name = serializers.CharField(source='floor.name', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    seats_used = serializers.IntegerField(read_only=True)
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lease
        fields = [
            'id', 'company', 'company_name', 'building', 'building_name',
            'floor', 'floor_name', 'seats_leased', 'seats_used', 'seats_available',
            'start_date', 'end_date', 'monthly_rate',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date.'})
        return attrs
