from rest_framework import serializers
from .models import JobPosting, Applicant, Application, Interview


class JobPostingSerializer(serializers.ModelSerializer):
    department_name  = serializers.CharField(source='department.name', read_only=True)
    created_by_name  = serializers.CharField(source='created_by.get_full_name', read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model  = JobPosting
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_application_count(self, obj):
        return obj.applications.count()


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Applicant
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name   = serializers.CharField(source='applicant.__str__', read_only=True)
    job_title        = serializers.CharField(source='job_posting.title', read_only=True)
    interview_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Application
        fields = '__all__'
        read_only_fields = ['applied_at', 'updated_at']

    def get_interview_count(self, obj):
        return obj.interviews.count()

    def validate(self, data):
        job = data.get('job_posting') or getattr(self.instance, 'job_posting', None)
        if job and job.status != 'open':
            raise serializers.ValidationError("Applications are only accepted for open job postings.")
        return data


class ApplicationAdvanceSerializer(serializers.Serializer):
    STATUS_ORDER = ['applied', 'screening', 'interview', 'offer', 'hired']

    status = serializers.ChoiceField(choices=['screening', 'interview', 'offer', 'hired', 'rejected'])
    notes  = serializers.CharField(required=False, allow_blank=True)


class InterviewSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='application.applicant.__str__', read_only=True)
    job_title      = serializers.CharField(source='application.job_posting.title', read_only=True)
    interviewer_name = serializers.CharField(source='interviewer.get_full_name', read_only=True)

    class Meta:
        model  = Interview
        fields = '__all__'
        read_only_fields = ['created_at']
