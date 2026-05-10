from rest_framework import serializers
from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    work_hours    = serializers.FloatField(read_only=True)

    class Meta:
        model  = AttendanceRecord
        fields = [
            'id',
            'employee',
            'employee_name',
            'date',
            'check_in',
            'check_out',
            'work_hours',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        check_in  = data.get('check_in',  getattr(self.instance, 'check_in',  None))
        check_out = data.get('check_out', getattr(self.instance, 'check_out', None))
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({'check_out': 'Check-out must be after check-in.'})
        return data
