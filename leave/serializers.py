from rest_framework import serializers
from django.utils import timezone
from .models import LeaveType, LeaveBalance, LeaveRequest, PublicHoliday


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    remaining_days = serializers.ReadOnlyField()
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['employee', 'status', 'reviewed_by',
                            'review_note', 'reviewed_at', 'total_days']

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')

        if start and end:
            if end < start:
                raise serializers.ValidationError("End date must be after start date.")
            if start < timezone.now().date():
                raise serializers.ValidationError("Cannot apply leave for past dates.")

        return data

    def create(self, validated_data):
        # auto-calculate total_days
        start = validated_data['start_date']
        end = validated_data['end_date']
        delta = (end - start).days + 1
        validated_data['total_days'] = delta
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)


class LeaveApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approved', 'rejected'])
    review_note = serializers.CharField(required=False, allow_blank=True)


class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = '__all__'