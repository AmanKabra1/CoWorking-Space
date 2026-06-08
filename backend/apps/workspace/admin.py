from django.contrib import admin
from .models import Building, Floor, Room, Desk, ParkingSlot


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'total_floors', 'total_desks', 'occupancy_rate', 'is_active']
    list_filter = ['city', 'state', 'is_active']
    search_fields = ['name', 'address', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 0
    fields = ['floor_number', 'name', 'is_active']
    readonly_fields = ['id']


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['name', 'floor_number', 'building', 'total_desks', 'occupied_desks', 'is_active']
    list_filter = ['building', 'is_active']
    search_fields = ['name', 'building__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['building', 'floor_number']


class DeskInline(admin.TabularInline):
    model = Desk
    extra = 0
    fields = ['desk_code', 'desk_type', 'company', 'monthly_rate', 'is_available']
    readonly_fields = ['id']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'name', 'room_type', 'floor', 'capacity', 'total_desks', 'available_desks', 'is_active']
    list_filter = ['room_type', 'floor__building', 'is_active']
    search_fields = ['room_number', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [DeskInline]


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['desk_code', 'desk_type', 'room', 'company', 'monthly_rate', 'is_available', 'is_assigned']
    list_filter = ['desk_type', 'is_available', 'room__floor__building', 'company']
    search_fields = ['desk_code', 'company__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['company']


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ['slot_number', 'slot_type', 'building', 'company', 'monthly_rate', 'is_available']
    list_filter = ['slot_type', 'is_available', 'building', 'company']
    search_fields = ['slot_number', 'company__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
