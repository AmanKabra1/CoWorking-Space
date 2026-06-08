from rest_framework import serializers
from .models import Building, Floor, Room, Desk, ParkingSlot


# ─── Building ─────────────────────────────────────────────

class BuildingListSerializer(serializers.ModelSerializer):
    total_floors = serializers.IntegerField(read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    occupied_desks = serializers.IntegerField(read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Building
        fields = [
            'id', 'name', 'city', 'state', 'is_active',
            'total_floors', 'total_desks', 'occupied_desks', 'occupancy_rate',
            'created_at',
        ]


class BuildingSerializer(serializers.ModelSerializer):
    total_floors = serializers.IntegerField(read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    occupied_desks = serializers.IntegerField(read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Building
        fields = [
            'id', 'name', 'address', 'city', 'state', 'pincode',
            'description', 'is_active',
            'total_floors', 'total_desks', 'occupied_desks', 'occupancy_rate',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ─── Floor ────────────────────────────────────────────────

class FloorListSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    occupied_desks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Floor
        fields = [
            'id', 'building', 'building_name',
            'floor_number', 'name', 'is_active',
            'total_desks', 'occupied_desks', 'created_at',
        ]


class FloorSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    occupied_desks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Floor
        fields = [
            'id', 'building', 'building_name',
            'floor_number', 'name', 'floor_plan', 'is_active',
            'total_desks', 'occupied_desks',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        building = attrs.get('building', getattr(self.instance, 'building', None))
        floor_number = attrs.get('floor_number', getattr(self.instance, 'floor_number', None))
        qs = Floor.objects.filter(building=building, floor_number=floor_number)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'floor_number': 'This floor number already exists in the building.'}
            )
        return attrs


# ─── Room ─────────────────────────────────────────────────

class RoomListSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    building_name = serializers.CharField(source='floor.building.name', read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    available_desks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'floor', 'floor_name', 'building_name',
            'room_number', 'name', 'room_type', 'capacity',
            'total_desks', 'available_desks', 'is_active', 'created_at',
        ]


class RoomSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    building_name = serializers.CharField(source='floor.building.name', read_only=True)
    total_desks = serializers.IntegerField(read_only=True)
    available_desks = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'floor', 'floor_name', 'building_name',
            'room_number', 'name', 'room_type', 'capacity', 'area_sqft',
            'total_desks', 'available_desks', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        floor = attrs.get('floor', getattr(self.instance, 'floor', None))
        room_number = attrs.get('room_number', getattr(self.instance, 'room_number', None))
        qs = Room.objects.filter(floor=floor, room_number=room_number)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'room_number': 'This room number already exists on the floor.'}
            )
        return attrs


# ─── Desk ─────────────────────────────────────────────────

class DeskSerializer(serializers.ModelSerializer):
    room_name = serializers.SerializerMethodField()
    floor_name = serializers.CharField(source='room.floor.name', read_only=True)
    building_name = serializers.CharField(source='room.floor.building.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True, default=None)
    is_assigned = serializers.BooleanField(read_only=True)

    class Meta:
        model = Desk
        fields = [
            'id', 'room', 'room_name', 'floor_name', 'building_name',
            'desk_code', 'desk_type', 'company', 'company_name',
            'monthly_rate', 'is_available', 'is_assigned', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_room_name(self, obj):
        return obj.room.name or obj.room.room_number

    def validate(self, attrs):
        room = attrs.get('room', getattr(self.instance, 'room', None))
        desk_code = attrs.get('desk_code', getattr(self.instance, 'desk_code', None))
        qs = Desk.objects.filter(room=room, desk_code=desk_code)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'desk_code': 'This desk code already exists in the room.'}
            )
        return attrs


class AssignDeskSerializer(serializers.Serializer):
    company = serializers.UUIDField(help_text='UUID of the company to assign this desk to')


# ─── Parking Slot ─────────────────────────────────────────

class ParkingSlotSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True, default=None)

    class Meta:
        model = ParkingSlot
        fields = [
            'id', 'building', 'building_name',
            'slot_number', 'slot_type', 'company', 'company_name',
            'monthly_rate', 'is_available', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        building = attrs.get('building', getattr(self.instance, 'building', None))
        slot_number = attrs.get('slot_number', getattr(self.instance, 'slot_number', None))
        qs = ParkingSlot.objects.filter(building=building, slot_number=slot_number)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'slot_number': 'This slot number already exists in the building.'}
            )
        return attrs


class AssignParkingSerializer(serializers.Serializer):
    company = serializers.UUIDField(help_text='UUID of the company to assign this slot to')
