import django_filters
from .models import LeaveRequest, LeaveBalance

class LeaveRequestFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date   = django_filters.DateFilter(field_name='end_date',   lookup_expr='lte')
    status     = django_filters.CharFilter(field_name='status')
    employee   = django_filters.NumberFilter(field_name='employee__id')
    leave_type = django_filters.NumberFilter(field_name='leave_type__id')

    class Meta:
        model = LeaveRequest
        fields = ['status', 'leave_type', 'employee', 'start_date', 'end_date']

class LeaveBalanceFilter(django_filters.FilterSet):
    year     = django_filters.NumberFilter(field_name='year')
    employee = django_filters.NumberFilter(field_name='employee__id')

    class Meta:
        model = LeaveBalance
        fields = ['year', 'leave_type', 'employee']