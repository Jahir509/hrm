from django.db import models
from django.conf import settings


class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('draft',  'Draft'),
        ('open',   'Open'),
        ('closed', 'Closed'),
    ]

    title       = models.CharField(max_length=200)
    department  = models.ForeignKey('core.Department', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    requirements= models.TextField(blank=True)
    vacancies   = models.PositiveIntegerField(default=1)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    deadline    = models.DateField(null=True, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='job_postings',
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class Applicant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    phone      = models.CharField(max_length=20, blank=True)
    resume     = models.FileField(upload_to='resumes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied',    'Applied'),
        ('screening',  'Screening'),
        ('interview',  'Interview'),
        ('offer',      'Offer'),
        ('hired',      'Hired'),
        ('rejected',   'Rejected'),
    ]

    job_posting  = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant    = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='applications')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_letter = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    applied_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job_posting', 'applicant')

    def __str__(self):
        return f"{self.applicant} → {self.job_posting.title} [{self.status}]"


class Interview(models.Model):
    MODE_CHOICES = [
        ('online',    'Online'),
        ('in_person', 'In Person'),
        ('phone',     'Phone'),
    ]
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('passed',  'Passed'),
        ('failed',  'Failed'),
    ]

    application  = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='interviews_conducted',
    )
    scheduled_at = models.DateTimeField()
    mode         = models.CharField(max_length=15, choices=MODE_CHOICES, default='online')
    venue        = models.CharField(max_length=255, blank=True)
    notes        = models.TextField(blank=True)
    result       = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.application.applicant} for {self.application.job_posting.title} @ {self.scheduled_at}"
