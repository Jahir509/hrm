from django.db import models
from django.conf import settings


class Event(models.Model):
    TYPE_CHOICES = [
        ('meeting',     'Meeting'),
        ('training',    'Training'),
        ('celebration', 'Celebration'),
        ('announcement','Announcement'),
        ('other',       'Other'),
    ]

    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)

    departments = models.ManyToManyField(
        'core.Department', blank=True, related_name='events'
    )
    is_company_wide = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.title} ({self.start_datetime.date()})"


class EventAttendee(models.Model):
    RSVP_CHOICES = [
        ('invited',  'Invited'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('attended', 'Attended'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_attendances'
    )
    rsvp_status = models.CharField(max_length=20, choices=RSVP_CHOICES, default='invited')
    responded_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('event', 'employee')

    def __str__(self):
        return f"{self.employee} — {self.event.title} ({self.rsvp_status})"
