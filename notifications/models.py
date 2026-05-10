from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_LEAVE = 'leave'
    TYPE_ATTENDANCE = 'attendance'
    TYPE_PAYROLL = 'payroll'
    TYPE_PERFORMANCE = 'performance'
    TYPE_RECRUITMENT = 'recruitment'
    TYPE_TRAINING = 'training'
    TYPE_SYSTEM = 'system'

    NOTIFICATION_TYPES = [
        (TYPE_LEAVE, 'Leave'),
        (TYPE_ATTENDANCE, 'Attendance'),
        (TYPE_PAYROLL, 'Payroll'),
        (TYPE_PERFORMANCE, 'Performance'),
        (TYPE_RECRUITMENT, 'Recruitment'),
        (TYPE_TRAINING, 'Training'),
        (TYPE_SYSTEM, 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default=TYPE_SYSTEM
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.notification_type}] {self.title} → {self.recipient}'
