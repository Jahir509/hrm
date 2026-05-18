from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.rbac import rbac
from .models import Notification
from .serializers import NotificationSerializer
from .filters import NotificationFilter

Employee = get_user_model()


# ── Notification List / Create ────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def notification_list(request):
    if request.method == 'GET':
        qs = Notification.objects.filter(recipient=request.user)
        filterset = NotificationFilter(request.GET, queryset=qs)
        return Response(NotificationSerializer(filterset.qs, many=True).data)

    # POST is restricted to admin and hr_manager
    user_role = getattr(request.user, 'role', None)
    if not user_role or user_role.name not in ('admin', 'hr_manager'):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Notification Detail / Delete ──────────────────────────────────────────────

@rbac(['GET', 'DELETE'])
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

    if request.method == 'GET':
        return Response(NotificationSerializer(notification).data)

    notification.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Mark Single Notification as Read ─────────────────────────────────────────

@rbac(['POST'])
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

    if notification.is_read:
        return Response({'detail': 'Notification is already marked as read.'})

    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save(update_fields=['is_read', 'read_at'])
    return Response(NotificationSerializer(notification).data)


# ── Mark All Notifications as Read ───────────────────────────────────────────

@rbac(['POST'])
def notification_mark_all_read(request):
    updated = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True, read_at=timezone.now())
    return Response({'detail': f'{updated} notification(s) marked as read.'})


# ── Unread Count ──────────────────────────────────────────────────────────────

@rbac(['GET'])
def notification_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': count})


# ── Broadcast ─────────────────────────────────────────────────────────────────

@rbac(['POST'])
def notification_broadcast(request):
    """
    Send the same notification to many recipients in one call.

    Body:
      {
        "title": str,
        "message": str,
        "notification_type": str (one of NOTIFICATION_TYPES),
        "recipients": [int, ...]   # omit / null / [] → all active employees
      }
    """
    user_role = getattr(request.user, 'role', None)
    if not user_role or user_role.name not in ('admin', 'hr_manager'):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    title = (request.data.get('title') or '').strip()
    message = (request.data.get('message') or '').strip()
    notification_type = request.data.get('notification_type') or Notification.TYPE_SYSTEM

    errors = {}
    if not title:
        errors['title'] = ['This field is required.']
    if not message:
        errors['message'] = ['This field is required.']
    valid_types = {key for key, _ in Notification.NOTIFICATION_TYPES}
    if notification_type not in valid_types:
        errors['notification_type'] = [f'Must be one of {sorted(valid_types)}.']
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    recipients = request.data.get('recipients')
    if recipients:
        recipient_qs = Employee.objects.filter(id__in=recipients, is_active=True)
    else:
        recipient_qs = Employee.objects.filter(is_active=True)

    created = Notification.objects.bulk_create([
        Notification(
            recipient=emp,
            title=title,
            message=message,
            notification_type=notification_type,
        )
        for emp in recipient_qs
    ])

    return Response(
        {'created': len(created), 'recipients': len(created)},
        status=status.HTTP_201_CREATED,
    )
