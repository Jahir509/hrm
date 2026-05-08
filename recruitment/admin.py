from django.contrib import admin
from .models import JobPosting, Applicant, Application, Interview


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'department', 'status', 'vacancies', 'deadline', 'created_at')
    list_filter   = ('status', 'department')
    search_fields = ('title',)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display  = ('first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_posting', 'status', 'applied_at')
    list_filter  = ('status',)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'interviewer', 'scheduled_at', 'mode', 'result')
    list_filter  = ('result', 'mode')
