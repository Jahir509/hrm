import django_filters
from .models import Event, EventAttendee


class EventFilter(django_filters.FilterSet):
    event_type       = django_filters.CharFilter(field_name='event_type')
    status           = django_filters.CharFilter(field_name='status')
    is_company_wide  = django_filters.BooleanFilter(field_name='is_company_wide')
    department       = django_filters.NumberFilter(field_name='departments__id')
    created_by       = django_filters.NumberFilter(field_name='created_by__id')
    start_from       = django_filters.DateFilter(field_name='start_datetime__date', lookup_expr='gte')
    start_until      = django_filters.DateFilter(field_name='start_datetime__date', lookup_expr='lte')

    class Meta:
        model = Event
        fields = ['event_type', 'status', 'is_company_wide', 'department', 'created_by', 'start_from', 'start_until']


class EventAttendeeFilter(django_filters.FilterSet):
    event      = django_filters.NumberFilter(field_name='event__id')
    employee   = django_filters.NumberFilter(field_name='employee__id')
    rsvp_status = django_filters.CharFilter(field_name='rsvp_status')

    class Meta:
        model = EventAttendee
        fields = ['event', 'employee', 'rsvp_status']
