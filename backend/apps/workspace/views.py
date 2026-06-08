from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Building, Floor, Room, Desk, ParkingSlot
from .serializers import (
    BuildingSerializer, BuildingListSerializer,
    FloorSerializer, FloorListSerializer,
    RoomSerializer, RoomListSerializer,
    DeskSerializer, AssignDeskSerializer,
    ParkingSlotSerializer, AssignParkingSerializer,
)
from .permissions import IsWorkspaceAdminOrReadOnly
from apps.accounts.permissions import IsSuperAdmin
from apps.companies.models import Company


# ─── Building ─────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Workspace — Buildings']),
    retrieve=extend_schema(tags=['Workspace — Buildings']),
    create=extend_schema(tags=['Workspace — Buildings']),
    update=extend_schema(tags=['Workspace — Buildings']),
    partial_update=extend_schema(tags=['Workspace — Buildings']),
    destroy=extend_schema(tags=['Workspace — Buildings']),
)
class BuildingViewSet(viewsets.ModelViewSet):
    """
    Manage physical buildings.
    Super Admin: full CRUD. Others: read-only.
    """
    permission_classes = [IsWorkspaceAdminOrReadOnly]
    filterset_fields = ['city', 'state', 'is_active']
    search_fields = ['name', 'city', 'address']

    def get_queryset(self):
        return Building.objects.filter(is_active=True)

    def get_serializer_class(self):
        return BuildingListSerializer if self.action == 'list' else BuildingSerializer

    @extend_schema(tags=['Workspace — Buildings'])
    @action(detail=True, methods=['get'], url_path='floors')
    def floors(self, request, pk=None):
        """List all active floors in this building."""
        building = self.get_object()
        qs = building.floors.filter(is_active=True).order_by('floor_number')
        serializer = FloorListSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Workspace — Buildings'])
    @action(detail=True, methods=['get'], url_path='occupancy')
    def occupancy(self, request, pk=None):
        """Desk occupancy breakdown for this building, per floor."""
        building = self.get_object()
        floors = building.floors.filter(is_active=True).order_by('floor_number')

        total_desks = 0
        occupied_desks = 0
        by_floor = []

        for floor in floors:
            all_desks = Desk.objects.filter(room__floor=floor)
            ft = all_desks.count()
            fo = all_desks.filter(company__isnull=False).count()
            total_desks += ft
            occupied_desks += fo
            by_floor.append({
                'floor_id': str(floor.id),
                'floor_number': floor.floor_number,
                'floor_name': floor.name,
                'total_desks': ft,
                'occupied_desks': fo,
                'available_desks': ft - fo,
                'occupancy_rate': round(fo / ft * 100, 1) if ft else 0.0,
            })

        available_desks = total_desks - occupied_desks
        return Response({
            'building_id': str(building.id),
            'building_name': building.name,
            'total_desks': total_desks,
            'occupied_desks': occupied_desks,
            'available_desks': available_desks,
            'occupancy_rate': round(occupied_desks / total_desks * 100, 1) if total_desks else 0.0,
            'by_floor': by_floor,
        })

    @extend_schema(tags=['Workspace — Buildings'])
    @action(detail=True, methods=['get'], url_path='parking')
    def parking(self, request, pk=None):
        """List all parking slots in this building."""
        building = self.get_object()
        qs = building.parking_slots.select_related('company').order_by('slot_number')
        serializer = ParkingSlotSerializer(qs, many=True)
        return Response(serializer.data)


# ─── Floor ────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Workspace — Floors']),
    retrieve=extend_schema(tags=['Workspace — Floors']),
    create=extend_schema(tags=['Workspace — Floors']),
    update=extend_schema(tags=['Workspace — Floors']),
    partial_update=extend_schema(tags=['Workspace — Floors']),
    destroy=extend_schema(tags=['Workspace — Floors']),
)
class FloorViewSet(viewsets.ModelViewSet):
    """
    Manage floors within buildings.
    Super Admin: full CRUD. Others: read-only.
    """
    permission_classes = [IsWorkspaceAdminOrReadOnly]
    filterset_fields = ['building', 'is_active']
    search_fields = ['name']

    def get_queryset(self):
        return Floor.objects.select_related('building').filter(is_active=True)

    def get_serializer_class(self):
        return FloorListSerializer if self.action == 'list' else FloorSerializer

    @extend_schema(tags=['Workspace — Floors'])
    @action(detail=True, methods=['get'], url_path='rooms')
    def rooms(self, request, pk=None):
        """List all active rooms on this floor."""
        floor = self.get_object()
        qs = floor.rooms.filter(is_active=True).order_by('room_number')
        serializer = RoomListSerializer(qs, many=True)
        return Response(serializer.data)


# ─── Room ─────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Workspace — Rooms']),
    retrieve=extend_schema(tags=['Workspace — Rooms']),
    create=extend_schema(tags=['Workspace — Rooms']),
    update=extend_schema(tags=['Workspace — Rooms']),
    partial_update=extend_schema(tags=['Workspace — Rooms']),
    destroy=extend_schema(tags=['Workspace — Rooms']),
)
class RoomViewSet(viewsets.ModelViewSet):
    """
    Manage rooms within floors.
    Super Admin: full CRUD. Others: read-only.
    """
    permission_classes = [IsWorkspaceAdminOrReadOnly]
    filterset_fields = ['floor', 'room_type', 'is_active']
    search_fields = ['room_number', 'name']

    def get_queryset(self):
        return Room.objects.select_related('floor__building').filter(is_active=True)

    def get_serializer_class(self):
        return RoomListSerializer if self.action == 'list' else RoomSerializer

    @extend_schema(tags=['Workspace — Rooms'])
    @action(detail=True, methods=['get'], url_path='desks')
    def desks(self, request, pk=None):
        """List all desks in this room."""
        room = self.get_object()
        qs = room.desks.select_related('company').order_by('desk_code')
        serializer = DeskSerializer(qs, many=True)
        return Response(serializer.data)


# ─── Desk ─────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Workspace — Desks']),
    retrieve=extend_schema(tags=['Workspace — Desks']),
    create=extend_schema(tags=['Workspace — Desks']),
    update=extend_schema(tags=['Workspace — Desks']),
    partial_update=extend_schema(tags=['Workspace — Desks']),
    destroy=extend_schema(tags=['Workspace — Desks']),
)
class DeskViewSet(viewsets.ModelViewSet):
    """
    Manage individual desks.
    Super Admin: full CRUD + assign/unassign. Others: read-only.
    """
    permission_classes = [IsWorkspaceAdminOrReadOnly]
    serializer_class = DeskSerializer
    filterset_fields = ['room', 'desk_type', 'company', 'is_available']
    search_fields = ['desk_code', 'notes']

    def get_queryset(self):
        return Desk.objects.select_related(
            'room__floor__building', 'company'
        ).order_by('room', 'desk_code')

    @extend_schema(
        tags=['Workspace — Desks'],
        request=AssignDeskSerializer,
        responses={200: DeskSerializer},
    )
    @action(detail=True, methods=['post'], url_path='assign', permission_classes=[IsSuperAdmin])
    def assign(self, request, pk=None):
        """
        Assign a dedicated desk to a company.
        Sets is_available=False and links the company.
        """
        desk = self.get_object()
        serializer = AssignDeskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            company = Company.objects.get(
                id=serializer.validated_data['company'], status=Company.ACTIVE
            )
        except Company.DoesNotExist:
            return Response(
                {'detail': 'Active company not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        desk.company = company
        desk.is_available = False
        desk.save(update_fields=['company', 'is_available', 'updated_at'])
        return Response(DeskSerializer(desk).data)

    @extend_schema(tags=['Workspace — Desks'], responses={200: DeskSerializer})
    @action(detail=True, methods=['post'], url_path='unassign', permission_classes=[IsSuperAdmin])
    def unassign(self, request, pk=None):
        """Remove a desk's company assignment and mark it available."""
        desk = self.get_object()
        desk.company = None
        desk.is_available = True
        desk.save(update_fields=['company', 'is_available', 'updated_at'])
        return Response(DeskSerializer(desk).data)


# ─── Parking Slot ─────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Workspace — Parking']),
    retrieve=extend_schema(tags=['Workspace — Parking']),
    create=extend_schema(tags=['Workspace — Parking']),
    update=extend_schema(tags=['Workspace — Parking']),
    partial_update=extend_schema(tags=['Workspace — Parking']),
    destroy=extend_schema(tags=['Workspace — Parking']),
)
class ParkingSlotViewSet(viewsets.ModelViewSet):
    """
    Manage parking slots per building.
    Super Admin: full CRUD + assign/unassign. Others: read-only.
    """
    permission_classes = [IsWorkspaceAdminOrReadOnly]
    serializer_class = ParkingSlotSerializer
    filterset_fields = ['building', 'slot_type', 'company', 'is_available']
    search_fields = ['slot_number', 'notes']

    def get_queryset(self):
        return ParkingSlot.objects.select_related('building', 'company').order_by(
            'building', 'slot_number'
        )

    @extend_schema(
        tags=['Workspace — Parking'],
        request=AssignParkingSerializer,
        responses={200: ParkingSlotSerializer},
    )
    @action(detail=True, methods=['post'], url_path='assign', permission_classes=[IsSuperAdmin])
    def assign(self, request, pk=None):
        """Assign a parking slot to a company."""
        slot = self.get_object()
        serializer = AssignParkingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            company = Company.objects.get(
                id=serializer.validated_data['company'], status=Company.ACTIVE
            )
        except Company.DoesNotExist:
            return Response(
                {'detail': 'Active company not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        slot.company = company
        slot.is_available = False
        slot.save(update_fields=['company', 'is_available', 'updated_at'])
        return Response(ParkingSlotSerializer(slot).data)

    @extend_schema(tags=['Workspace — Parking'], responses={200: ParkingSlotSerializer})
    @action(detail=True, methods=['post'], url_path='unassign', permission_classes=[IsSuperAdmin])
    def unassign(self, request, pk=None):
        """Remove a parking slot's assignment."""
        slot = self.get_object()
        slot.company = None
        slot.is_available = True
        slot.save(update_fields=['company', 'is_available', 'updated_at'])
        return Response(ParkingSlotSerializer(slot).data)
