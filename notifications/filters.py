import django_filters
from .models import Notification


class NotificationFilter(django_filters.FilterSet):
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Notification
        fields = ['is_read', 'notification_type', 'created_after', 'created_before']
