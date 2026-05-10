import django_filters
from .models import AttendanceRecord


class AttendanceFilter(django_filters.FilterSet):
    date_from   = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to     = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    employee_id = django_filters.NumberFilter(field_name='employee__id')

    class Meta:
        model  = AttendanceRecord
        fields = ['status', 'employee_id', 'date_from', 'date_to']
