from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.rbac import rbac
from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday
from .serializers import (
    LeaveTypeSerializer, LeaveBalanceSerializer,
    LeaveRequestSerializer, LeaveApprovalSerializer,
    PublicHolidaySerializer,
)
from .filters import LeaveRequestFilter, LeaveBalanceFilter


# ── Leave Types ───────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def leave_type_list(request):
    if request.method == 'GET':
        qs = LeaveType.objects.filter(is_active=True)
        return Response(LeaveTypeSerializer(qs, many=True).data)

    serializer = LeaveTypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def leave_type_detail(request, pk):
    leave_type = get_object_or_404(LeaveType, pk=pk)

    if request.method == 'GET':
        return Response(LeaveTypeSerializer(leave_type).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = LeaveTypeSerializer(leave_type, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    leave_type.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Leave Balances ────────────────────────────────────────────────────────────

@rbac(['GET'], public=True)
def leave_balance_list(request):
    qs = LeaveBalance.objects.select_related('employee', 'leave_type').all()
    filterset = LeaveBalanceFilter(request.GET, queryset=qs)
    return Response(LeaveBalanceSerializer(filterset.qs, many=True).data)


@rbac(['GET'], public=True)
def leave_balance_detail(request, pk):
    balance = get_object_or_404(LeaveBalance, pk=pk)
    return Response(LeaveBalanceSerializer(balance).data)


# ── Leave Requests ────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def leave_request_list(request):
    if request.method == 'GET':
        qs = LeaveRequest.objects.select_related('employee', 'leave_type', 'reviewed_by').all()
        filterset = LeaveRequestFilter(request.GET, queryset=qs)
        return Response(LeaveRequestSerializer(filterset.qs, many=True).data)

    serializer = LeaveRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def leave_request_detail(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == 'GET':
        return Response(LeaveRequestSerializer(leave).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = LeaveRequestSerializer(
            leave, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    leave.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['POST'], public=True)
def leave_request_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if leave.status != 'pending':
        return Response(
            {'detail': 'Only pending requests can be reviewed.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = LeaveApprovalSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    taken = serializer.validated_data['action']
    leave.status = taken
    leave.reviewed_by = request.user if request.user.is_authenticated else None
    leave.review_note = serializer.validated_data.get('review_note', '')
    leave.reviewed_at = timezone.now()
    leave.save()

    if taken == 'approved':
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=leave.employee,
            leave_type=leave.leave_type,
            year=leave.start_date.year,
            defaults={'allocated_days': leave.leave_type.max_days_per_year},
        )
        balance.used_days += leave.total_days
        balance.save()

    return Response({'detail': f'Leave {taken} successfully.'})


@rbac(['POST'], public=True)
def leave_request_cancel(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if leave.status != 'pending':
        return Response(
            {'detail': 'Only pending requests can be cancelled.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    leave.status = 'cancelled'
    leave.save()
    return Response({'detail': 'Leave request cancelled.'})


@rbac(['GET'], public=True)
def my_leave_requests(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    qs = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    return Response(LeaveRequestSerializer(qs, many=True).data)


# ── Public Holidays ───────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def public_holiday_list(request):
    if request.method == 'GET':
        qs = PublicHoliday.objects.all().order_by('date')
        return Response(PublicHolidaySerializer(qs, many=True).data)

    serializer = PublicHolidaySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def public_holiday_detail(request, pk):
    holiday = get_object_or_404(PublicHoliday, pk=pk)

    if request.method == 'GET':
        return Response(PublicHolidaySerializer(holiday).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = PublicHolidaySerializer(holiday, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    holiday.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
