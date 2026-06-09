from django.contrib import admin
from .models import InventoryItem, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    fields = ['direction', 'quantity', 'reason', 'performed_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'building', 'quantity', 'unit',
        'reorder_level', 'is_low_stock', 'is_active',
    ]
    list_filter = ['category', 'building', 'is_active']
    search_fields = ['name', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_low_stock']
    inlines = [StockMovementInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['item', 'direction', 'quantity', 'performed_by', 'created_at']
    list_filter = ['direction', 'created_at']
    search_fields = ['item__name', 'reason']
    readonly_fields = ['id', 'created_at', 'updated_at']
