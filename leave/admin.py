from django.contrib import admin
from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_days_per_year', 'carry_forward', 'is_active']

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days']
    list_filter = ['year', 'leave_type']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__first_name', 'employee__last_name']

@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    ordering = ['date']