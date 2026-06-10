from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.permissions import IsSuperAdminOrCompanyAdmin
from apps.core.exporters import build_export_response
from .models import InventoryItem, StockMovement
from .serializers import (
    InventoryItemSerializer,
    StockMovementSerializer,
    StockAdjustSerializer,
)


def _leased_building_ids(user):
    """Building IDs the user's company occupies (via desks or parking)."""
    from apps.workspace.models import Desk, ParkingSlot
    if not user.company_id:
        return []
    desk_ids = Desk.objects.filter(
        company_id=user.company_id
    ).values_list('room__floor__building_id', flat=True)
    park_ids = ParkingSlot.objects.filter(
        company_id=user.company_id
    ).values_list('building_id', flat=True)
    return list(set(desk_ids) | set(park_ids))


@extend_schema_view(
    list=extend_schema(tags=['Inventory']),
    retrieve=extend_schema(tags=['Inventory']),
    create=extend_schema(tags=['Inventory']),
    update=extend_schema(tags=['Inventory']),
    partial_update=extend_schema(tags=['Inventory']),
    destroy=extend_schema(tags=['Inventory']),
)
class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    Building inventory — pantry, canteen, water, appliances, etc.

    - Super Admin: all buildings.
    - Company Admin: only buildings their company occupies.
    Restock / consume via custom actions, which log a StockMovement.
    """

    serializer_class = InventoryItemSerializer
    permission_classes = [IsSuperAdminOrCompanyAdmin]
    filterset_fields = ['building', 'category', 'is_active']
    search_fields = ['name', 'notes']

    def get_queryset(self):
        user = self.request.user
        qs = InventoryItem.objects.select_related('building')
        if user.is_super_admin:
            return qs
        return qs.filter(building_id__in=_leased_building_ids(user))

    @extend_schema(tags=['Inventory'], request=StockAdjustSerializer, responses={200: InventoryItemSerializer})
    @action(detail=True, methods=['post'], url_path='restock')
    def restock(self, request, pk=None):
        """Add stock (stock-in) and log the movement."""
        return self._adjust(request, InventoryItem, StockMovement.IN)

    @extend_schema(tags=['Inventory'], request=StockAdjustSerializer, responses={200: InventoryItemSerializer})
    @action(detail=True, methods=['post'], url_path='consume')
    def consume(self, request, pk=None):
        """Remove stock (stock-out) and log the movement."""
        return self._adjust(request, InventoryItem, StockMovement.OUT)

    def _adjust(self, request, _model, direction):
        item = self.get_object()
        serializer = StockAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']
        reason = serializer.validated_data.get('reason', '')

        if direction == StockMovement.OUT:
            if qty > item.quantity:
                return Response(
                    {'detail': f'Cannot consume {qty}; only {item.quantity} {item.unit} in stock.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            item.quantity -= qty
        else:
            item.quantity += qty

        item.save(update_fields=['quantity', 'updated_at'])
        StockMovement.objects.create(
            item=item, direction=direction, quantity=qty,
            reason=reason, performed_by=request.user,
        )
        return Response(InventoryItemSerializer(item).data)

    @extend_schema(tags=['Inventory'], responses={200: InventoryItemSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Items at or below their reorder level."""
        items = [i for i in self.get_queryset() if i.is_low_stock]
        return Response(InventoryItemSerializer(items, many=True).data)

    @extend_schema(tags=['Inventory'], responses={200: StockMovementSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='movements')
    def movements(self, request, pk=None):
        """Stock-movement history for one item."""
        item = self.get_object()
        qs = item.movements.select_related('performed_by').all()
        return Response(StockMovementSerializer(qs, many=True).data)

    @extend_schema(tags=['Inventory'])
    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """Download the inventory list as Excel / Word / PDF (?format=excel|word|pdf)."""
        items = self.filter_queryset(self.get_queryset())
        headers = ['Item', 'Category', 'Building', 'Quantity', 'Unit', 'Reorder Level', 'Unit Cost', 'Low Stock']
        rows = [
            [
                i.name, i.get_category_display(), i.building.name,
                i.quantity, i.unit, i.reorder_level, i.unit_cost,
                'Yes' if i.is_low_stock else 'No',
            ]
            for i in items
        ]
        return build_export_response(
            request.query_params.get('fmt'),
            'inventory', 'CoWorkHub — Inventory', headers, rows,
        )
