from django.db import models
from django.conf import settings

class LeaveType(models.Model):
    name = models.CharField(max_length=100)          # Annual, Sick, Maternity
    max_days_per_year = models.PositiveIntegerField()
    carry_forward = models.BooleanField(default=False)
    carry_forward_max_days = models.PositiveIntegerField(default=0)
    requires_document = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_balances'
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    allocated_days = models.FloatField(default=0)
    used_days = models.FloatField(default=0)
    carried_forward_days = models.FloatField(default=0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    @property
    def remaining_days(self):
        return self.allocated_days + self.carried_forward_days - self.used_days

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.year})"


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled','Cancelled'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests'
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.FloatField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    document = models.FileField(upload_to='leave_docs/', null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_leaves'
    )
    review_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} | {self.leave_type} | {self.status}"


class PublicHoliday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.date})"