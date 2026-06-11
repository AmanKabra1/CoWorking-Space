from django.db import models
from apps.core.models import TimeStampedModel


class Facility(TimeStampedModel):
    CONFERENCE_ROOM = 'conference_room'
    MEETING_ROOM = 'meeting_room'
    EVENT_HALL = 'event_hall'
    PODCAST_STUDIO = 'podcast_studio'
    PRINTING_ROOM = 'printing_room'
    THREE_D_PRINTER = '3d_printer'
    CAFETERIA = 'cafeteria'
    OTHER = 'other'

    TYPE_CHOICES = [
        (CONFERENCE_ROOM, 'Conference Room'),
        (MEETING_ROOM, 'Meeting Room'),
        (EVENT_HALL, 'Event Hall'),
        (PODCAST_STUDIO, 'Podcast Studio'),
        (PRINTING_ROOM, 'Printing Room'),
        (THREE_D_PRINTER, '3D Printer'),
        (CAFETERIA, 'Cafeteria'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    building = models.ForeignKey(
        'workspace.Building', on_delete=models.CASCADE, related_name='facilities'
    )
    floor = models.ForeignKey(
        'workspace.Floor', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='facilities',
    )
    # Null = building-wide facility owned by the operator (super admin).
    # Set = a facility a company added (for its team and/or the public).
    owner_company = models.ForeignKey(
        'companies.Company', on_delete=models.CASCADE,
        null=True, blank=True, related_name='owned_facilities',
    )
    capacity = models.PositiveIntegerField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    amenities = models.JSONField(
        default=list, blank=True,
        help_text='List of amenities, e.g. ["WiFi", "Projector", "AC", "Whiteboard"]',
    )
    booking_rules = models.JSONField(
        default=dict, blank=True,
        help_text='e.g. {"min_hours": 1, "max_hours": 8, "advance_days": 1, "cancellation_hours": 24}',
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(
        default=False,
        help_text='If true, external visitors can book this facility without logging in.',
    )

    class Meta:
        db_table = 'facilities_facility'
        ordering = ['name']
        verbose_name_plural = 'facilities'

    def __str__(self):
        return f'{self.name} ({self.get_facility_type_display()})'


class FacilityImage(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='facility_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'facilities_facilityimage'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.facility.name} — Image #{self.order}'
