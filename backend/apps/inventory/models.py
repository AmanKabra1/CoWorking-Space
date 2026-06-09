from django.db import models
from apps.core.models import TimeStampedModel


class InventoryItem(TimeStampedModel):
    """
    A consumable or asset stocked at a building — pantry supplies, canteen
    stock, water bottles, daily appliances, cleaning material, stationery, etc.
    """

    PANTRY = 'pantry'
    CANTEEN = 'canteen'
    WATER = 'water'
    APPLIANCE = 'appliance'
    CLEANING = 'cleaning'
    STATIONERY = 'stationery'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (PANTRY, 'Pantry'),
        (CANTEEN, 'Canteen'),
        (WATER, 'Water / Beverages'),
        (APPLIANCE, 'Daily Appliance'),
        (CLEANING, 'Cleaning Supplies'),
        (STATIONERY, 'Stationery'),
        (OTHER, 'Other'),
    ]

    building = models.ForeignKey(
        'workspace.Building', on_delete=models.CASCADE, related_name='inventory_items'
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=OTHER)
    unit = models.CharField(
        max_length=30, default='pcs',
        help_text='Unit of measure, e.g. pcs, kg, litre, packet, box',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='Stock at or below this level is flagged as low.',
    )
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'inventory_item'
        ordering = ['building', 'category', 'name']
        verbose_name = 'inventory item'
        verbose_name_plural = 'inventory items'

    def __str__(self):
        return f'{self.name} ({self.get_category_display()}) — {self.building.name}'

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class StockMovement(TimeStampedModel):
    """An audit log of every stock change — restock (in) or consumption (out)."""

    IN = 'in'
    OUT = 'out'

    DIRECTION_CHOICES = [
        (IN, 'Stock In (Restock)'),
        (OUT, 'Stock Out (Consume)'),
    ]

    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name='movements'
    )
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_movements',
    )

    class Meta:
        db_table = 'inventory_stockmovement'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_direction_display()} {self.quantity} — {self.item.name}'
