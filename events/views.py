import calendar as cal_module
from datetime import date, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status

from accounts.rbac import rbac
from .models import Event, EventAttendee
from .serializers import EventSerializer, EventAttendeeSerializer, RSVPSerializer
from .filters import EventFilter, EventAttendeeFilter


# ── Events ────────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def event_list(request):
    if request.method == 'GET':
        qs = Event.objects.prefetch_related('departments', 'attendees').all()
        qs = EventFilter(request.GET, queryset=qs).qs
        return Response(EventSerializer(qs, many=True, context={'request': request}).data)

    serializer = EventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'GET':
        return Response(EventSerializer(event, context={'request': request}).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = EventSerializer(
            event, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    event.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Attendees ─────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def event_attendee_list(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'GET':
        qs = event.attendees.select_related('employee').all()
        qs = EventAttendeeFilter(request.GET, queryset=qs).qs
        return Response(EventAttendeeSerializer(qs, many=True).data)

    data = {**request.data, 'event': event.pk}
    serializer = EventAttendeeSerializer(data=data)
    if serializer.is_valid():
        serializer.save(event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PATCH', 'DELETE'])
def event_attendee_detail(request, pk, att_pk):
    attendee = get_object_or_404(EventAttendee, pk=att_pk, event__pk=pk)

    if request.method == 'GET':
        return Response(EventAttendeeSerializer(attendee).data)

    if request.method == 'PATCH':
        serializer = EventAttendeeSerializer(attendee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    attendee.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── RSVP ──────────────────────────────────────────────────────────────────────

@rbac(['POST'])
def event_rsvp(request, pk):
    """Logged-in employee accepts or declines an event."""
    event = get_object_or_404(Event, pk=pk)

    serializer = RSVPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    attendee, _ = EventAttendee.objects.get_or_create(
        event=event, employee=request.user
    )
    attendee.rsvp_status = serializer.validated_data['rsvp_status']
    attendee.note = serializer.validated_data.get('note', attendee.note)
    attendee.responded_at = timezone.now()
    attendee.save()

    return Response(EventAttendeeSerializer(attendee).data)


# ── My Events ─────────────────────────────────────────────────────────────────

@rbac(['GET'])
def my_events(request):
    """Events the current user has been added to as an attendee."""
    qs = EventAttendee.objects.filter(employee=request.user).select_related('event')
    qs = EventAttendeeFilter(request.GET, queryset=qs).qs
    return Response(EventAttendeeSerializer(qs, many=True).data)


# ── My Calendar ───────────────────────────────────────────────────────────────

@rbac(['GET'])
def my_calendar(request):
    """
    Returns all events visible to the current user for a given month.

    Query params:
        year  (int, default: current year)
        month (int, default: current month)

    Response:
        year, month, month_name, total_days,
        events (flat list),
        by_date (dict keyed by day-of-month string)
    """
    now = timezone.localtime(timezone.now())
    try:
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
        if not (1 <= month <= 12):
            raise ValueError
    except ValueError:
        return Response({'detail': 'Invalid year or month.'}, status=status.HTTP_400_BAD_REQUEST)

    _, total_days = cal_module.monthrange(year, month)
    first_day = date(year, month, 1)
    last_day = date(year, month, total_days)

    user = request.user
    qs = Event.objects.filter(
        status='published',
        start_datetime__date__lte=last_day,
        end_datetime__date__gte=first_day,
    ).filter(
        Q(is_company_wide=True)
        | Q(departments=getattr(user, 'department', None))
        | Q(attendees__employee=user)
    ).distinct().prefetch_related('departments', 'attendees')

    serialized = EventSerializer(qs, many=True, context={'request': request}).data

    by_date = {}
    for event_data, event_obj in zip(serialized, qs):
        span_start = max(event_obj.start_datetime.date(), first_day)
        span_end = min(event_obj.end_datetime.date(), last_day)
        current = span_start
        while current <= span_end:
            day_key = str(current.day)
            by_date.setdefault(day_key, []).append(event_data)
            current += timedelta(days=1)

    return Response({
        'year': year,
        'month': month,
        'month_name': cal_module.month_name[month],
        'total_days': total_days,
        'events': serialized,
        'by_date': by_date,
    })
