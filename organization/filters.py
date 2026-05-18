import django_filters
from .models import Organization, Branch, Holiday, WorkSchedule, OrganizationDocument


class OrganizationFilter(django_filters.FilterSet):
    name    = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model  = Organization
        fields = ['name', 'organization_type', 'size', 'status', 'industry', 'country']


class BranchFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model  = Branch
        fields = ['organization', 'branch_type', 'is_active', 'city', 'country', 'name']


class HolidayFilter(django_filters.FilterSet):
    date_after  = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model  = Holiday
        fields = ['organization', 'branch', 'is_recurring', 'date_after', 'date_before']


class WorkScheduleFilter(django_filters.FilterSet):
    class Meta:
        model  = WorkSchedule
        fields = ['organization', 'is_default']


class OrganizationDocumentFilter(django_filters.FilterSet):
    class Meta:
        model  = OrganizationDocument
        fields = ['organization', 'document_type']
