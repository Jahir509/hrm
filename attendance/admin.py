from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ('id', 'employee', 'date', 'status', 'check_in', 'check_out', 'work_hours')
    list_filter   = ('status', 'date')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    readonly_fields = ('created_at', 'updated_at')
