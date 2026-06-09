from decimal import Decimal
from rest_framework import serializers
from .models import InventoryItem, StockMovement


class InventoryItemSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'building', 'building_name', 'name',
            'category', 'category_display', 'unit',
            'quantity', 'reorder_level', 'unit_cost',
            'is_low_stock', 'notes', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'direction', 'direction_display',
            'quantity', 'reason', 'performed_by', 'performed_by_name',
            'created_at',
        ]
        read_only_fields = ['id', 'performed_by', 'created_at']

    def get_performed_by_name(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else None


class StockAdjustSerializer(serializers.Serializer):
    """Payload for the restock / consume actions."""

    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value
