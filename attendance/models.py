from django.db import models
from django.conf import settings


class AttendanceRecord(models.Model):
    STATUS_PRESENT  = 'present'
    STATUS_ABSENT   = 'absent'
    STATUS_LATE     = 'late'
    STATUS_HALF_DAY = 'half_day'
    STATUS_ON_LEAVE = 'on_leave'
    STATUS_HOLIDAY  = 'holiday'

    STATUS_CHOICES = [
        (STATUS_PRESENT,  'Present'),
        (STATUS_ABSENT,   'Absent'),
        (STATUS_LATE,     'Late'),
        (STATUS_HALF_DAY, 'Half Day'),
        (STATUS_ON_LEAVE, 'On Leave'),
        (STATUS_HOLIDAY,  'Holiday'),
    ]

    employee   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date       = models.DateField()
    check_in   = models.DateTimeField(null=True, blank=True)
    check_out  = models.DateTimeField(null=True, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee']

    def __str__(self):
        return f'{self.employee} | {self.date} | {self.status}'

    @property
    def work_hours(self):
        """Decimal hours worked; None if check-in or check-out is missing."""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return round(delta.total_seconds() / 3600, 2)
        return None
