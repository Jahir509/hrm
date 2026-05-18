from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.rbac import rbac
from utils.permissions import is_admin
from .models import (
    Organization,
    Branch,
    Holiday,
    WorkSchedule,
    OrganizationDocument,
    SocialLink,
)
from .serializers import (
    OrganizationSerializer,
    BranchSerializer,
    HolidaySerializer,
    WorkScheduleSerializer,
    OrganizationDocumentSerializer,
    SocialLinkSerializer,
)
from .filters import (
    OrganizationFilter,
    BranchFilter,
    HolidayFilter,
    WorkScheduleFilter,
    OrganizationDocumentFilter,
)


def _forbidden():
    return Response(
        {'detail': 'You do not have permission to perform this action.'},
        status=status.HTTP_403_FORBIDDEN,
    )


# ── Organizations ─────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def organization_list(request):
    if request.method == 'GET':
        filterset = OrganizationFilter(
            request.GET,
            queryset=Organization.objects.select_related('ceo', 'owner').all(),
        )
        return Response(OrganizationSerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return _forbidden()

    serializer = OrganizationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def organization_detail(request, pk):
    organization = get_object_or_404(Organization, pk=pk)

    if request.method == 'GET':
        return Response(OrganizationSerializer(organization).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = OrganizationSerializer(
            organization, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    organization.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['GET'],public=True)
def primary_organization(request):
    organization = Organization.objects.filter(is_primary=True).exists()
    if not organization:
        return Response({'detail': 'No primary organization configured.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(organization)


# ── Branches ─────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def branch_list(request):
    if request.method == 'GET':
        filterset = BranchFilter(
            request.GET,
            queryset=Branch.objects.select_related('organization', 'manager').all(),
        )
        return Response(BranchSerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return _forbidden()

    serializer = BranchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def branch_detail(request, pk):
    branch = get_object_or_404(Branch, pk=pk)

    if request.method == 'GET':
        return Response(BranchSerializer(branch).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = BranchSerializer(
            branch, data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    branch.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['GET'])
def organization_branches(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    filterset = BranchFilter(
        request.GET,
        queryset=Branch.objects.filter(organization=organization).select_related('manager'),
    )
    return Response(BranchSerializer(filterset.qs, many=True).data)


# ── Holidays ─────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def holiday_list(request):
    if request.method == 'GET':
        filterset = HolidayFilter(
            request.GET,
            queryset=Holiday.objects.select_related('organization', 'branch').all(),
        )
        return Response(HolidaySerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return _forbidden()

    serializer = HolidaySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def holiday_detail(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)

    if request.method == 'GET':
        return Response(HolidaySerializer(holiday).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = HolidaySerializer(
            holiday, data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    holiday.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Work schedules ───────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def work_schedule_list(request):
    if request.method == 'GET':
        filterset = WorkScheduleFilter(
            request.GET,
            queryset=WorkSchedule.objects.select_related('organization').all(),
        )
        return Response(WorkScheduleSerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return _forbidden()

    serializer = WorkScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def work_schedule_detail(request, pk):
    schedule = get_object_or_404(WorkSchedule, pk=pk)

    if request.method == 'GET':
        return Response(WorkScheduleSerializer(schedule).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = WorkScheduleSerializer(
            schedule, data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    schedule.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Documents ────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def document_list(request):
    if request.method == 'GET':
        filterset = OrganizationDocumentFilter(
            request.GET,
            queryset=OrganizationDocument.objects.select_related('organization', 'uploaded_by').all(),
        )
        return Response(OrganizationDocumentSerializer(filterset.qs, many=True).data)

    if not is_admin(request.user):
        return _forbidden()

    serializer = OrganizationDocumentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def document_detail(request, pk):
    document = get_object_or_404(OrganizationDocument, pk=pk)

    if request.method == 'GET':
        return Response(OrganizationDocumentSerializer(document).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = OrganizationDocumentSerializer(
            document, data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    document.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Social links ─────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'])
def social_link_list(request):
    if request.method == 'GET':
        return Response(
            SocialLinkSerializer(SocialLink.objects.select_related('organization').all(), many=True).data
        )

    if not is_admin(request.user):
        return _forbidden()

    serializer = SocialLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'])
def social_link_detail(request, pk):
    link = get_object_or_404(SocialLink, pk=pk)

    if request.method == 'GET':
        return Response(SocialLinkSerializer(link).data)

    if not is_admin(request.user):
        return _forbidden()

    if request.method in ('PUT', 'PATCH'):
        serializer = SocialLinkSerializer(
            link, data=request.data,
            partial=request.method == 'PATCH',
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    link.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
