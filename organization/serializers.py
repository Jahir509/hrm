from rest_framework import serializers
from .models import (
    Organization,
    Branch,
    Holiday,
    WorkSchedule,
    OrganizationDocument,
    SocialLink,
)


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SocialLink
        fields = ['id', 'organization', 'platform', 'url']


class OrganizationSerializer(serializers.ModelSerializer):
    ceo_name      = serializers.CharField(source='ceo.get_full_name',   read_only=True)
    owner_name    = serializers.CharField(source='owner.get_full_name', read_only=True)
    branch_count  = serializers.IntegerField(source='branches.count',   read_only=True)
    social_links  = SocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model  = Organization
        fields = [
            'id',
            'name', 'legal_name', 'short_name', 'slug',
            'registration_number', 'tax_id',
            'industry', 'organization_type', 'size', 'founded_date',
            'logo', 'favicon', 'primary_color', 'secondary_color',
            'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code',
            'description', 'mission', 'vision',
            'currency', 'timezone', 'fiscal_year_start',
            'weekly_working_days', 'weekly_working_hours',
            'ceo', 'ceo_name', 'owner', 'owner_name',
            'status', 'is_primary',
            'branch_count', 'social_links',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_primary_color(self, value):
        if value and not value.startswith('#'):
            raise serializers.ValidationError('Color must be a hex code starting with #.')
        return value

    def validate(self, data):
        if data.get('is_primary'):
            qs = Organization.objects.filter(is_primary=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'is_primary': 'Another organization is already marked as primary.'}
                )
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BranchSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    manager_name      = serializers.CharField(source='manager.get_full_name', read_only=True)

    class Meta:
        model  = Branch
        fields = [
            'id', 'organization', 'organization_name',
            'name', 'code', 'branch_type',
            'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code',
            'timezone',
            'manager', 'manager_name',
            'opened_on', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class HolidaySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    branch_name       = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model  = Holiday
        fields = [
            'id', 'organization', 'organization_name',
            'branch', 'branch_name',
            'name', 'date', 'is_recurring', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        branch = data.get('branch', getattr(self.instance, 'branch', None))
        organization = data.get('organization', getattr(self.instance, 'organization', None))
        if branch and organization and branch.organization_id != organization.id:
            raise serializers.ValidationError(
                {'branch': 'Branch does not belong to the given organization.'}
            )
        return data


class WorkScheduleSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model  = WorkSchedule
        fields = [
            'id', 'organization', 'organization_name',
            'name', 'start_time', 'end_time', 'break_minutes',
            'works_monday', 'works_tuesday', 'works_wednesday', 'works_thursday',
            'works_friday', 'works_saturday', 'works_sunday',
            'is_default',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        start = data.get('start_time', getattr(self.instance, 'start_time', None))
        end   = data.get('end_time',   getattr(self.instance, 'end_time',   None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {'end_time': 'End time must be after start time.'}
            )
        return data


class OrganizationDocumentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    uploaded_by_name  = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model  = OrganizationDocument
        fields = [
            'id', 'organization', 'organization_name',
            'title', 'document_type', 'file', 'description',
            'effective_date', 'expiry_date',
            'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
