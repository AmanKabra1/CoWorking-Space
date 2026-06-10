from rest_framework import serializers
from .models import SeatLease


class SeatLeaseSerializer(serializers.ModelSerializer):
    desk_code = serializers.CharField(source='desk.desk_code', read_only=True)
    desk_location = serializers.CharField(source='desk.room.__str__', read_only=True)
    lessor_company_name = serializers.CharField(source='lessor_company.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SeatLease
        fields = [
            'id', 'desk', 'desk_code', 'desk_location',
            'lessor_company', 'lessor_company_name',
            'lessee_name', 'lessee_email', 'lessee_phone', 'lessee_company',
            'start_date', 'end_date', 'monthly_rate',
            'status', 'status_display', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'lessor_company', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        desk = attrs.get('desk') or getattr(self.instance, 'desk', None)

        # Company admins may only sub-lease desks assigned to their own company.
        if desk is not None and not user.is_super_admin:
            if desk.company_id != user.company_id:
                raise serializers.ValidationError(
                    {'desk': 'You can only sub-lease desks assigned to your company.'}
                )

        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date.'})

        # Block overlapping active sub-leases for the same desk.
        if desk is not None:
            active = SeatLease.objects.filter(desk=desk, status=SeatLease.ACTIVE)
            if self.instance:
                active = active.exclude(pk=self.instance.pk)
            if active.exists():
                raise serializers.ValidationError(
                    {'desk': 'This desk already has an active sub-lease.'}
                )
        return attrs
