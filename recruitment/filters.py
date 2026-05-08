import django_filters
from .models import JobPosting, Application, Interview


class JobPostingFilter(django_filters.FilterSet):
    status     = django_filters.CharFilter(field_name='status')
    department = django_filters.NumberFilter(field_name='department__id')
    deadline   = django_filters.DateFilter(field_name='deadline', lookup_expr='lte')

    class Meta:
        model  = JobPosting
        fields = ['status', 'department', 'deadline']


class ApplicationFilter(django_filters.FilterSet):
    status      = django_filters.CharFilter(field_name='status')
    job_posting = django_filters.NumberFilter(field_name='job_posting__id')
    applicant   = django_filters.NumberFilter(field_name='applicant__id')

    class Meta:
        model  = Application
        fields = ['status', 'job_posting', 'applicant']


class InterviewFilter(django_filters.FilterSet):
    result      = django_filters.CharFilter(field_name='result')
    mode        = django_filters.CharFilter(field_name='mode')
    interviewer = django_filters.NumberFilter(field_name='interviewer__id')
    application = django_filters.NumberFilter(field_name='application__id')

    class Meta:
        model  = Interview
        fields = ['result', 'mode', 'interviewer', 'application']
