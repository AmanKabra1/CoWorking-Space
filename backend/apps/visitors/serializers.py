from rest_framework import serializers
from .models import VisitorPass


class VisitorPassSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = VisitorPass
        fields = [
            'id', 'company', 'company_name', 'visitor_name', 'visitor_email',
            'visitor_phone', 'purpose', 'host', 'host_name', 'building', 'building_name',
            'pass_code', 'status', 'scheduled_date', 'valid_from', 'valid_until',
            'checked_in_at', 'checked_out_at', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'pass_code', 'status', 'checked_in_at', 'checked_out_at',
            'created_by', 'created_at', 'updated_at',
        ]

    def validate(self, attrs):
        if attrs.get('valid_from') and attrs.get('valid_until'):
            if attrs['valid_from'] >= attrs['valid_until']:
                raise serializers.ValidationError("valid_until must be after valid_from.")
        return attrs

    def validate_company(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and user.company != value:
            raise serializers.ValidationError("You can only create passes for your own company.")
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class VisitorPassPublicSerializer(serializers.ModelSerializer):
    """Minimal read-only view for QR scan verification — no auth required."""
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = VisitorPass
        fields = [
            'visitor_name', 'purpose', 'host_name', 'building_name',
            'pass_code', 'status', 'scheduled_date', 'valid_from', 'valid_until',
        ]
