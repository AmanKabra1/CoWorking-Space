from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'company', 'company_name',
            'action', 'resource_type', 'resource_id', 'description',
            'ip_address', 'extra', 'created_at',
        ]
        read_only_fields = fields
