from django.db import models
from django.conf import settings


class Sprint(models.Model):
    STATUS_PLANNING   = 'planning'
    STATUS_ACTIVE     = 'active'
    STATUS_COMPLETED  = 'completed'
    STATUS_CANCELLED  = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PLANNING,  'Planning'),
        (STATUS_ACTIVE,    'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    name       = models.CharField(max_length=255)
    goal       = models.TextField(blank=True)
    start_date = models.DateField()
    end_date   = models.DateField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sprints_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} [{self.status}]'


class Task(models.Model):
    STATUS_TODO      = 'todo'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_DONE      = 'done'

    STATUS_CHOICES = [
        (STATUS_TODO,        'To Do'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_IN_REVIEW,   'In Review'),
        (STATUS_DONE,        'Done'),
    ]

    PRIORITY_LOW      = 'low'
    PRIORITY_MEDIUM   = 'medium'
    PRIORITY_HIGH     = 'high'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW,      'Low'),
        (PRIORITY_MEDIUM,   'Medium'),
        (PRIORITY_HIGH,     'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]

    sprint        = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='tasks')
    title         = models.CharField(max_length=255)
    description   = models.TextField(blank=True)
    assigned_to   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tasks',
    )
    created_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tasks_created',
    )
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    priority      = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    story_points  = models.PositiveIntegerField(null=True, blank=True)
    due_date      = models.DateField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'status', 'created_at']

    def __str__(self):
        return f'{self.title} [{self.status}]'
