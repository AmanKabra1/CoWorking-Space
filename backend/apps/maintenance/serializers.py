from rest_framework import serializers
from .models import MaintenanceTicket


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = MaintenanceTicket
        fields = [
            'id', 'ticket_number', 'company', 'company_name', 'building', 'building_name',
            'title', 'description', 'category', 'priority', 'status',
            'reported_by', 'reported_by_name', 'assigned_to', 'assigned_to_name',
            'image', 'resolved_at', 'resolution_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'ticket_number', 'reported_by', 'status',
            'resolved_at', 'created_at', 'updated_at',
        ]

    def validate_company(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and user.company != value:
            raise serializers.ValidationError("You can only create tickets for your own company.")
        return value

    def create(self, validated_data):
        validated_data['reported_by'] = self.context['request'].user
        return super().create(validated_data)


class AssignTicketSerializer(serializers.Serializer):
    assigned_to = serializers.UUIDField()


class ResolveTicketSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=False, allow_blank=True, default='')
