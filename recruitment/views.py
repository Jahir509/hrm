from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.rbac import rbac
from .models import JobPosting, Applicant, Application, Interview
from .serializers import (
    JobPostingSerializer, ApplicantSerializer,
    ApplicationSerializer, ApplicationAdvanceSerializer,
    InterviewSerializer,
)
from .filters import JobPostingFilter, ApplicationFilter, InterviewFilter


# ── Job Postings ──────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def job_posting_list(request):
    if request.method == 'GET':
        qs = JobPosting.objects.select_related('department', 'created_by').all()
        qs = JobPostingFilter(request.GET, queryset=qs).qs
        return Response(JobPostingSerializer(qs, many=True).data)

    serializer = JobPostingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user if request.user.is_authenticated else None)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def job_posting_detail(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)

    if request.method == 'GET':
        return Response(JobPostingSerializer(job).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = JobPostingSerializer(job, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    job.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['POST'], public=True)
def job_posting_close(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)
    if job.status == 'closed':
        return Response({'detail': 'Job posting is already closed.'}, status=status.HTTP_400_BAD_REQUEST)
    job.status = 'closed'
    job.save()
    return Response({'detail': 'Job posting closed.'})


# ── Applicants ────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def applicant_list(request):
    if request.method == 'GET':
        qs = Applicant.objects.all()
        return Response(ApplicantSerializer(qs, many=True).data)

    serializer = ApplicantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def applicant_detail(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)

    if request.method == 'GET':
        return Response(ApplicantSerializer(applicant).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = ApplicantSerializer(applicant, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    applicant.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Applications ──────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def application_list(request):
    if request.method == 'GET':
        qs = Application.objects.select_related('job_posting', 'applicant').all()
        qs = ApplicationFilter(request.GET, queryset=qs).qs
        return Response(ApplicationSerializer(qs, many=True).data)

    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'GET':
        return Response(ApplicationSerializer(application).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = ApplicationSerializer(
            application, data=request.data, partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@rbac(['POST'], public=True)
def application_advance(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status in ('hired', 'rejected'):
        return Response(
            {'detail': f'Application is already {application.status}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ApplicationAdvanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    application.status = serializer.validated_data['status']
    if serializer.validated_data.get('notes'):
        application.notes = serializer.validated_data['notes']
    application.save()
    return Response({'detail': f'Application moved to {application.status}.'})


# ── Interviews ────────────────────────────────────────────────────────────────

@rbac(['GET', 'POST'], public=True)
def interview_list(request):
    if request.method == 'GET':
        qs = Interview.objects.select_related('application', 'interviewer').all()
        qs = InterviewFilter(request.GET, queryset=qs).qs
        return Response(InterviewSerializer(qs, many=True).data)

    serializer = InterviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@rbac(['GET', 'PUT', 'PATCH', 'DELETE'], public=True)
def interview_detail(request, pk):
    interview = get_object_or_404(Interview, pk=pk)

    if request.method == 'GET':
        return Response(InterviewSerializer(interview).data)

    if request.method in ('PUT', 'PATCH'):
        serializer = InterviewSerializer(interview, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    interview.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
