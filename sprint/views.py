from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.rbac import rbac
from utils.permissions import is_admin
from .models import Sprint, Task
from .serializers import SprintSerializer, TaskSerializer, TaskStatusSerializer
from .filters import SprintFilter, TaskFilter


# ── Sprints ───────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def sprint_list(request):
    if request.method == 'GET':
        filterset = SprintFilter(request.GET, queryset=Sprint.objects.select_related('created_by').all())
        return Response(SprintSerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = SprintSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def sprint_detail(request, pk):
    sprint = get_object_or_404(Sprint, pk=pk)

    if request.method == 'GET':
        return Response(SprintSerializer(sprint).data)

    if not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ('PUT', 'PATCH'):
        serializer = SprintSerializer(
            sprint, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    sprint.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['POST'])
def sprint_activate(request, pk):
    if not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    sprint = get_object_or_404(Sprint, pk=pk)

    if sprint.status != Sprint.STATUS_PLANNING:
        return Response(
            {'detail': 'Only a sprint in planning can be activated.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Ensure no other sprint is currently active
    if Sprint.objects.filter(status=Sprint.STATUS_ACTIVE).exists():
        return Response(
            {'detail': 'Another sprint is already active. Complete it before activating a new one.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sprint.status = Sprint.STATUS_ACTIVE
    sprint.save(update_fields=['status', 'updated_at'])
    return Response(SprintSerializer(sprint).data)


@rbac(['POST'])
def sprint_complete(request, pk):
    if not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    sprint = get_object_or_404(Sprint, pk=pk)

    if sprint.status != Sprint.STATUS_ACTIVE:
        return Response(
            {'detail': 'Only an active sprint can be completed.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sprint.status = Sprint.STATUS_COMPLETED
    sprint.save(update_fields=['status', 'updated_at'])
    return Response(SprintSerializer(sprint).data)


# ── Tasks ─────────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        filterset = TaskFilter(
            request.GET,
            queryset=Task.objects.select_related('sprint', 'assigned_to', 'created_by').all(),
        )
        return Response(TaskSerializer(filterset.qs, many=True).data)

    serializer = TaskSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'GET':
        return Response(TaskSerializer(task).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = TaskSerializer(
            task, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['POST'])
def task_move(request, pk):
    """Move a task to a different status column."""
    task = get_object_or_404(Task, pk=pk)

    if task.assigned_to != request.user and not is_admin(request.user):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = TaskStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    task.status = serializer.validated_data['status']
    task.save(update_fields=['status', 'updated_at'])
    return Response(TaskSerializer(task).data)


@rbac(['GET'])
def my_tasks(request):
    """Current user's assigned tasks, optionally filtered."""
    filterset = TaskFilter(
        request.GET,
        queryset=Task.objects.filter(assigned_to=request.user).select_related('sprint'),
    )
    return Response(TaskSerializer(filterset.qs, many=True).data)


@rbac(['GET'])
def sprint_tasks(request, pk):
    """All tasks belonging to a specific sprint."""
    sprint = get_object_or_404(Sprint, pk=pk)
    filterset = TaskFilter(
        request.GET,
        queryset=Task.objects.filter(sprint=sprint).select_related('assigned_to', 'created_by'),
    )
    return Response(TaskSerializer(filterset.qs, many=True).data)
