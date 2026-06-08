from django.db import models
from apps.core.models import TimeStampedModel


class Building(TimeStampedModel):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspace_building'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_floors(self):
        return self.floors.filter(is_active=True).count()

    @property
    def total_desks(self):
        return Desk.objects.filter(room__floor__building=self).count()

    @property
    def occupied_desks(self):
        return Desk.objects.filter(room__floor__building=self, company__isnull=False).count()

    @property
    def occupancy_rate(self):
        total = self.total_desks
        return round(self.occupied_desks / total * 100, 1) if total else 0.0


class Floor(TimeStampedModel):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField(help_text='0 = Ground Floor, 1 = 1st Floor, etc.')
    name = models.CharField(max_length=100, help_text='e.g. Ground Floor, 1st Floor')
    floor_plan = models.ImageField(upload_to='floor_plans/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspace_floor'
        ordering = ['building', 'floor_number']
        unique_together = [['building', 'floor_number']]

    def __str__(self):
        return f'{self.building.name} — {self.name}'

    @property
    def total_desks(self):
        return Desk.objects.filter(room__floor=self).count()

    @property
    def occupied_desks(self):
        return Desk.objects.filter(room__floor=self, company__isnull=False).count()


class Room(TimeStampedModel):
    CABIN = 'cabin'
    OPEN_SPACE = 'open_space'
    MEETING_ROOM = 'meeting_room'
    EVENT_HALL = 'event_hall'
    STORAGE = 'storage'
    OTHER = 'other'

    ROOM_TYPE_CHOICES = [
        (CABIN, 'Private Cabin'),
        (OPEN_SPACE, 'Open Space'),
        (MEETING_ROOM, 'Meeting Room'),
        (EVENT_HALL, 'Event Hall'),
        (STORAGE, 'Storage'),
        (OTHER, 'Other'),
    ]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20, help_text='e.g. 101, A-205')
    name = models.CharField(max_length=100, blank=True, help_text='Optional display name')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default=OPEN_SPACE)
    capacity = models.PositiveIntegerField(default=1)
    area_sqft = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'workspace_room'
        ordering = ['floor', 'room_number']
        unique_together = [['floor', 'room_number']]

    def __str__(self):
        label = self.name or self.room_number
        return f'{self.floor} — {label}'

    @property
    def total_desks(self):
        return self.desks.count()

    @property
    def available_desks(self):
        return self.desks.filter(company__isnull=True, is_available=True).count()


class Desk(TimeStampedModel):
    DEDICATED = 'dedicated'
    HOT_DESK = 'hot_desk'

    DESK_TYPE_CHOICES = [
        (DEDICATED, 'Dedicated Desk'),
        (HOT_DESK, 'Hot Desk'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='desks')
    desk_code = models.CharField(max_length=20, help_text='e.g. D-101-A, HOT-01')
    desk_type = models.CharField(max_length=20, choices=DESK_TYPE_CHOICES, default=HOT_DESK)
    company = models.ForeignKey(
        'companies.Company',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_desks',
        help_text='Set for dedicated desks — which company this desk belongs to',
    )
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(
        default=True,
        help_text='False if desk is under maintenance or permanently occupied',
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'workspace_desk'
        ordering = ['room', 'desk_code']
        unique_together = [['room', 'desk_code']]

    def __str__(self):
        return f'{self.desk_code} ({self.get_desk_type_display()}) — {self.room}'

    @property
    def is_assigned(self):
        return self.company_id is not None


class ParkingSlot(TimeStampedModel):
    CAR = 'car'
    BIKE = 'bike'
    EV = 'ev'

    SLOT_TYPE_CHOICES = [
        (CAR, 'Car'),
        (BIKE, 'Bike / Scooter'),
        (EV, 'EV Charging'),
    ]

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='parking_slots')
    slot_number = models.CharField(max_length=20, help_text='e.g. P-01, B-15, EV-03')
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPE_CHOICES, default=CAR)
    company = models.ForeignKey(
        'companies.Company',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_parking',
    )
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'workspace_parkingslot'
        ordering = ['building', 'slot_number']
        unique_together = [['building', 'slot_number']]

    def __str__(self):
        return f'{self.slot_number} ({self.get_slot_type_display()}) — {self.building.name}'
