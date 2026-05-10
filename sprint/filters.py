import django_filters
from .models import Sprint, Task


class SprintFilter(django_filters.FilterSet):
    start_after  = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model  = Sprint
        fields = ['status', 'start_after', 'start_before']


class TaskFilter(django_filters.FilterSet):
    class Meta:
        model  = Task
        fields = ['sprint', 'status', 'priority', 'assigned_to']
