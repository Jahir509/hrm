"""
Dashboard rollup endpoints.

Aggregates counts and series from every HRM module into a single payload tuned
for the frontend dashboard. Read-only, scoped per user: admin/HR managers see
organization-wide numbers, regular employees see their own scope where it
matters (attendance, leave, tasks, notifications).
"""
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response

from accounts.rbac import rbac
from utils.permissions import is_admin

from attendance.models import AttendanceRecord
from events.models import Event
from leave.models import LeaveRequest, PublicHoliday
from notifications.models import Notification
from recruitment.models import Application, Interview, JobPosting
from sprint.models import Sprint, Task

Employee = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _month_bounds(reference=None):
    today = reference or timezone.localdate()
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return today, start, end


def _last_n_months(n=6):
    today = timezone.localdate().replace(day=1)
    months = []
    for i in range(n - 1, -1, -1):
        year, month = today.year, today.month - i
        while month <= 0:
            month += 12
            year -= 1
        months.append((year, month))
    return months


def _month_range(year, month):
    tz = timezone.get_current_timezone()
    start = timezone.datetime(year, month, 1, tzinfo=tz)
    if month == 12:
        end = start.replace(year=year + 1, month=1)
    else:
        end = start.replace(month=month + 1)
    return start, end


def _monthly_counts(qs, datetime_field, months):
    """Count records grouped by (year, month). Returns OrderedDict keyed YYYY-MM."""
    result = OrderedDict((f'{y:04d}-{m:02d}', 0) for y, m in months)
    for year, month in months:
        start, end = _month_range(year, month)
        result[f'{year:04d}-{month:02d}'] = qs.filter(
            **{f'{datetime_field}__gte': start, f'{datetime_field}__lt': end}
        ).count()
    return result


# ── Main rollup ───────────────────────────────────────────────────────────────

@rbac(['GET'])
def dashboard_overview(request):
    user = request.user
    admin = is_admin(user)
    today, month_start, month_end = _month_bounds()

    # ── Employees ────────────────────────────────────────────────────────────
    employee_qs = Employee.objects.all()
    employee_block = {
        'total': employee_qs.count(),
        'active': employee_qs.filter(is_active=True).count(),
        'inactive': employee_qs.filter(is_active=False).count(),
        'by_department': list(
            employee_qs.values('department__name')
            .annotate(value=Count('id'))
            .order_by('-value')
        ),
    }

    # ── Attendance (current month) ───────────────────────────────────────────
    att_qs = AttendanceRecord.objects.filter(
        date__gte=month_start, date__lt=month_end
    )
    if not admin:
        att_qs = att_qs.filter(employee=user)

    status_counts = {key: 0 for key, _ in AttendanceRecord.STATUS_CHOICES}
    for row in att_qs.values('status').annotate(value=Count('id')):
        status_counts[row['status']] = row['value']

    today_record = AttendanceRecord.objects.filter(employee=user, date=today).first()
    present_today = bool(today_record and today_record.check_in)

    total_days = sum(status_counts.values())
    present_days = status_counts.get('present', 0) + status_counts.get('late', 0)
    leave_days = status_counts.get('on_leave', 0)
    ratio = round(present_days / total_days * 100, 2) if total_days else 0.0

    attendance_block = {
        'today': present_today,
        'today_status': today_record.status if today_record else None,
        'presentDays': present_days,
        'totalDays': total_days,
        'leaveDays': leave_days,
        'ratio': ratio,
        'breakdown': status_counts,
    }

    # ── Leave ────────────────────────────────────────────────────────────────
    leave_qs = LeaveRequest.objects.all() if admin else LeaveRequest.objects.filter(employee=user)
    leave_status_counts = {choice: 0 for choice, _ in LeaveRequest.STATUS_CHOICES}
    for row in leave_qs.values('status').annotate(value=Count('id')):
        leave_status_counts[row['status']] = row['value']

    leave_month = leave_qs.filter(created_at__gte=month_start, created_at__lt=month_end)
    leave_block = {
        'total': leave_qs.count(),
        'applied': leave_month.count(),
        'pending': leave_status_counts.get('pending', 0),
        'approved': leave_status_counts.get('approved', 0),
        'rejected': leave_status_counts.get('rejected', 0),
        'cancelled': leave_status_counts.get('cancelled', 0),
        'breakdown': leave_status_counts,
    }

    # ── Recruitment ──────────────────────────────────────────────────────────
    jobs_qs = JobPosting.objects.all()
    apps_qs = Application.objects.all()
    interviews_qs = Interview.objects.all()

    jobs_block = {
        'total': jobs_qs.count(),
        'active': jobs_qs.filter(status='open').count(),
        'closed': jobs_qs.filter(status='closed').count(),
        'draft': jobs_qs.filter(status='draft').count(),
    }

    application_status_counts = {choice: 0 for choice, _ in Application.STATUS_CHOICES}
    for row in apps_qs.values('status').annotate(value=Count('id')):
        application_status_counts[row['status']] = row['value']

    candidates_block = {
        'total': apps_qs.count(),
        'active': apps_qs.exclude(status__in=['rejected', 'hired']).count(),
        'hired': application_status_counts.get('hired', 0),
        'rejected': application_status_counts.get('rejected', 0),
        'breakdown': application_status_counts,
    }

    recent_applications = []
    for app in apps_qs.select_related('applicant', 'job_posting').order_by('-applied_at')[:5]:
        recent_applications.append({
            'applicationId': app.id,
            'jobTitle': app.job_posting.title if app.job_posting_id else '',
            'candidateName': f'{app.applicant.first_name} {app.applicant.last_name}'.strip(),
            'project': app.status,
            'applied_at': app.applied_at,
        })

    upcoming_interviews = []
    for iv in interviews_qs.select_related(
        'application__applicant', 'application__job_posting'
    ).filter(scheduled_at__gte=timezone.now()).order_by('scheduled_at')[:8]:
        applicant = iv.application.applicant
        upcoming_interviews.append({
            'interviewId': iv.id,
            'candidateName': f'{applicant.first_name} {applicant.last_name}'.strip(),
            'jobTitle': iv.application.job_posting.title if iv.application.job_posting_id else '',
            'scheduledAt': iv.scheduled_at,
            'mode': iv.mode,
            'result': iv.result,
        })

    job_applications_block = {
        'total': apps_qs.count(),
        'recentApplied': recent_applications,
    }

    # ── Events ───────────────────────────────────────────────────────────────
    upcoming_events_qs = Event.objects.filter(
        start_datetime__gte=timezone.now(),
        status='published',
    ).order_by('start_datetime')[:5]

    office_events_block = {
        'total': Event.objects.filter(status='published').count(),
        'upcoming': [
            {
                'eventId': e.id,
                'title': e.title,
                'eventDate': e.start_datetime,
                'event_type': e.event_type,
                'location': e.location,
            }
            for e in upcoming_events_qs
        ],
    }

    # ── Sprint / Tasks ───────────────────────────────────────────────────────
    sprint_qs = Sprint.objects.all()
    task_qs = Task.objects.all() if admin else Task.objects.filter(assigned_to=user)
    task_status_counts = {key: 0 for key, _ in Task.STATUS_CHOICES}
    for row in task_qs.values('status').annotate(value=Count('id')):
        task_status_counts[row['status']] = row['value']

    sprint_block = {
        'total': sprint_qs.count(),
        'active': sprint_qs.filter(status='active').count(),
        'completed': sprint_qs.filter(status='completed').count(),
        'tasks': {
            'total': task_qs.count(),
            'breakdown': task_status_counts,
        },
    }

    # ── Notifications ────────────────────────────────────────────────────────
    notif_qs = Notification.objects.filter(recipient=user)
    notices_block = {
        'total': notif_qs.count(),
        'unread': notif_qs.filter(is_read=False).count(),
        'recent': [
            {
                'id': n.id,
                'title': n.title,
                'notification_type': n.notification_type,
                'created_at': n.created_at,
                'is_read': n.is_read,
            }
            for n in notif_qs.order_by('-created_at')[:5]
        ],
    }

    # ── 6-month trends ───────────────────────────────────────────────────────
    months = _last_n_months(6)
    apps_trend = _monthly_counts(apps_qs, 'applied_at', months)
    leave_trend = _monthly_counts(leave_qs, 'created_at', months)

    trends_block = {
        'months': list(apps_trend.keys()),
        'applications': list(apps_trend.values()),
        'leave_requests': list(leave_trend.values()),
    }

    # ── Public holidays ──────────────────────────────────────────────────────
    holidays_block = [
        {'name': h.name, 'date': h.date}
        for h in PublicHoliday.objects.filter(date__gte=today).order_by('date')[:5]
    ]

    return Response({
        'as_of': timezone.now(),
        'is_admin': admin,
        'employee': employee_block,
        'attendance': attendance_block,
        'leaveApplications': leave_block,
        'jobs': jobs_block,
        'candidates': candidates_block,
        'jobApplications': job_applications_block,
        'officeEvents': office_events_block,
        'sprints': sprint_block,
        'notices': notices_block,
        'upcomingInterviews': upcoming_interviews,
        'publicHolidays': holidays_block,
        'trends': trends_block,
    })
