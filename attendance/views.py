from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.rbac import rbac
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer
from .filters import AttendanceFilter

LATE_THRESHOLD_HOUR   = 9
LATE_THRESHOLD_MINUTE = 30

_ADMIN_ROLES = ('admin', 'hr_manager')


def _is_admin(user):
    role = getattr(user, 'role', None)
    return bool(role and role.name in _ADMIN_ROLES)


# ── List / Create ─────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def attendance_list(request):
    if request.method == 'GET':
        # admin/hr_manager: all records; employee: own records only
        qs = (
            AttendanceRecord.objects.select_related('employee').all()
            if _is_admin(request.user)
            else AttendanceRecord.objects.filter(employee=request.user)
        )
        filterset = AttendanceFilter(request.GET, queryset=qs)
        return Response(AttendanceRecordSerializer(filterset.qs, many=True).data)

    # POST — manual record creation (admin / hr_manager only)
    if not _is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AttendanceRecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Detail / Update / Delete ──────────────────────────────────────────────────

@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def attendance_detail(request, pk):
    record = get_object_or_404(AttendanceRecord, pk=pk)

    # employees may only view their own record
    if not _is_admin(request.user) and record.employee != request.user:
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'GET':
        return Response(AttendanceRecordSerializer(record).data)

    if request.method in ('PUT', 'PATCH'):
        if not _is_admin(request.user):
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AttendanceRecordSerializer(
            record, data=request.data, partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE — admin only
    if not _is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    record.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── My Attendance ─────────────────────────────────────────────────────────────

@rbac(['GET'])
def my_attendance(request):
    qs = AttendanceRecord.objects.filter(employee=request.user)
    filterset = AttendanceFilter(request.GET, queryset=qs)
    return Response(AttendanceRecordSerializer(filterset.qs, many=True).data)


# ── Check-In ──────────────────────────────────────────────────────────────────

@rbac(['POST'])
def attendance_check_in(request):
    today = timezone.localdate()
    now   = timezone.now()

    if AttendanceRecord.objects.filter(employee=request.user, date=today, check_in__isnull=False).exists():
        return Response(
            {'detail': 'Already checked in for today.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    local_now    = timezone.localtime(now)
    is_late      = (local_now.hour, local_now.minute) > (LATE_THRESHOLD_HOUR, LATE_THRESHOLD_MINUTE)
    record_status = AttendanceRecord.STATUS_LATE if is_late else AttendanceRecord.STATUS_PRESENT

    record, _ = AttendanceRecord.objects.get_or_create(
        employee=request.user,
        date=today,
        defaults={'status': record_status, 'check_in': now},
    )

    # If admin pre-created an absent record, update it
    if record.check_in is None:
        record.check_in = now
        record.status   = record_status
        record.save(update_fields=['check_in', 'status', 'updated_at'])

    return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_200_OK)


# ── Check-Out ─────────────────────────────────────────────────────────────────

@rbac(['POST'])
def attendance_check_out(request):
    today = timezone.localdate()
    now   = timezone.now()

    record = AttendanceRecord.objects.filter(employee=request.user, date=today).first()

    if not record or not record.check_in:
        return Response(
            {'detail': 'No check-in found for today. Please check in first.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if record.check_out:
        return Response(
            {'detail': 'Already checked out for today.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    record.check_out = now

    # Downgrade to half_day if worked fewer than 5 hours
    if record.check_in:
        hours_worked = (now - record.check_in).total_seconds() / 3600
        if hours_worked < 5 and record.status in (AttendanceRecord.STATUS_PRESENT, AttendanceRecord.STATUS_LATE):
            record.status = AttendanceRecord.STATUS_HALF_DAY

    record.save(update_fields=['check_out', 'status', 'updated_at'])
    return Response(AttendanceRecordSerializer(record).data)


# ── Monthly Summary ───────────────────────────────────────────────────────────

@rbac(['GET'])
def attendance_summary(request):
    today = timezone.localdate()
    year  = int(request.GET.get('year',  today.year))
    month = int(request.GET.get('month', today.month))

    qs = AttendanceRecord.objects.filter(
        employee=request.user,
        date__year=year,
        date__month=month,
    )

    counts = {choice: 0 for choice, _ in AttendanceRecord.STATUS_CHOICES}
    for record in qs:
        counts[record.status] += 1

    return Response({
        'year':     year,
        'month':    month,
        'total':    qs.count(),
        'present':  counts[AttendanceRecord.STATUS_PRESENT],
        'absent':   counts[AttendanceRecord.STATUS_ABSENT],
        'late':     counts[AttendanceRecord.STATUS_LATE],
        'half_day': counts[AttendanceRecord.STATUS_HALF_DAY],
        'on_leave': counts[AttendanceRecord.STATUS_ON_LEAVE],
        'holiday':  counts[AttendanceRecord.STATUS_HOLIDAY],
    })
