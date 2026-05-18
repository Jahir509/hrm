"""
Account-scoped endpoints.

`me` returns the enriched profile for the currently authenticated user — the
shape the frontend profile dashboard consumes (basic fields, role, department,
designation, photo, and lightweight aggregate stats across HRM modules).
"""
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.response import Response

from accounts.rbac import rbac
from attendance.models import AttendanceRecord
from leave.models import LeaveBalance, LeaveRequest
from notifications.models import Notification
from sprint.models import Task


def _month_bounds():
    today = timezone.localdate()
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return today, start, end


@rbac(['GET'])
def me(request):
    user = request.user
    today, month_start, month_end = _month_bounds()
    year = today.year

    # ── Profile fields ───────────────────────────────────────────────────────
    profile = {
        'id':                 user.id,
        'username':           user.username,
        'email':              user.email,
        'first_name':         user.first_name,
        'last_name':          user.last_name,
        'full_name':          f'{user.first_name} {user.last_name}'.strip() or user.username,
        'phone':              user.phone,
        'date_of_birth':      user.date_of_birth,
        'date_joined_company': user.date_joined_company,
        'is_active':          user.is_active,
        'is_staff':           user.is_staff,
        'last_login':         user.last_login,
        'date_joined':        user.date_joined,
        'profile_photo':      user.profile_photo.url if user.profile_photo else None,
        'role':               getattr(user.role, 'name', None) if user.role_id else None,
        'department':         {
            'id':   user.department_id,
            'name': getattr(user.department, 'name', None) if user.department_id else None,
        },
        'designation':        {
            'id':   user.designation_id,
            'name': getattr(user.designation, 'name', None) if user.designation_id else None,
        },
    }

    # ── Attendance (current month) ───────────────────────────────────────────
    att_month = AttendanceRecord.objects.filter(
        employee=user, date__gte=month_start, date__lt=month_end
    )
    today_rec = AttendanceRecord.objects.filter(employee=user, date=today).first()
    status_counts = {key: 0 for key, _ in AttendanceRecord.STATUS_CHOICES}
    for row in att_month.values('status').annotate(value=Count('id')):
        status_counts[row['status']] = row['value']
    total = sum(status_counts.values())
    present = status_counts.get('present', 0) + status_counts.get('late', 0)
    ratio = round(present / total * 100, 2) if total else 0.0

    attendance = {
        'today': bool(today_rec and today_rec.check_in),
        'today_status': today_rec.status if today_rec else None,
        'today_check_in': today_rec.check_in if today_rec else None,
        'today_check_out': today_rec.check_out if today_rec else None,
        'month_total':   total,
        'month_present': present,
        'month_absent':  status_counts.get('absent', 0),
        'month_leave':   status_counts.get('on_leave', 0),
        'month_late':    status_counts.get('late', 0),
        'month_ratio':   ratio,
    }

    # ── Leave (this calendar year + balances) ────────────────────────────────
    leave_qs = LeaveRequest.objects.filter(employee=user, created_at__year=year)
    leave_status = {choice: 0 for choice, _ in LeaveRequest.STATUS_CHOICES}
    for row in leave_qs.values('status').annotate(value=Count('id')):
        leave_status[row['status']] = row['value']

    balances = [
        {
            'leave_type':   lb.leave_type.name,
            'year':         lb.year,
            'allocated':    lb.allocated_days,
            'used':         lb.used_days,
            'carried':      lb.carried_forward_days,
            'remaining':    lb.remaining_days,
        }
        for lb in LeaveBalance.objects.filter(employee=user, year=year).select_related('leave_type')
    ]

    leave = {
        'total_this_year': leave_qs.count(),
        'pending':         leave_status.get('pending', 0),
        'approved':        leave_status.get('approved', 0),
        'rejected':        leave_status.get('rejected', 0),
        'cancelled':       leave_status.get('cancelled', 0),
        'balances':        balances,
        'recent': [
            {
                'id':          lr.id,
                'leave_type':  lr.leave_type.name,
                'start_date':  lr.start_date,
                'end_date':    lr.end_date,
                'total_days':  lr.total_days,
                'status':      lr.status,
                'reason':      lr.reason,
                'created_at':  lr.created_at,
            }
            for lr in leave_qs.select_related('leave_type').order_by('-created_at')[:5]
        ],
    }

    # ── Sprint tasks assigned to me ──────────────────────────────────────────
    task_qs = Task.objects.filter(assigned_to=user)
    task_counts = {key: 0 for key, _ in Task.STATUS_CHOICES}
    for row in task_qs.values('status').annotate(value=Count('id')):
        task_counts[row['status']] = row['value']

    tasks = {
        'total': task_qs.count(),
        'breakdown': task_counts,
        'open': task_qs.exclude(status='done').count(),
        'overdue': task_qs.filter(
            due_date__lt=today,
        ).exclude(status='done').count(),
        'recent': [
            {
                'id':       t.id,
                'title':    t.title,
                'status':   t.status,
                'priority': t.priority,
                'due_date': t.due_date,
                'sprint':   t.sprint.name if t.sprint_id else None,
            }
            for t in task_qs.select_related('sprint').order_by('-updated_at')[:5]
        ],
    }

    # ── Notifications ────────────────────────────────────────────────────────
    notif_qs = Notification.objects.filter(recipient=user)
    notifications = {
        'total':  notif_qs.count(),
        'unread': notif_qs.filter(is_read=False).count(),
    }

    return Response({
        'profile':      profile,
        'attendance':   attendance,
        'leave':        leave,
        'tasks':        tasks,
        'notifications': notifications,
    })
