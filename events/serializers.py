from rest_framework import serializers
from django.utils import timezone

from .models import Event, EventAttendee


class EventAttendeeSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = EventAttendee
        fields = '__all__'
        read_only_fields = ['employee', 'responded_at']


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    attendee_count = serializers.SerializerMethodField()
    department_names = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_attendee_count(self, obj):
        return obj.attendees.count()

    def get_department_names(self, obj):
        return list(obj.departments.values_list('name', flat=True))

    def validate(self, data):
        start = data.get('start_datetime')
        end = data.get('end_datetime')
        if start and end and end <= start:
            raise serializers.ValidationError("end_datetime must be after start_datetime.")
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class RSVPSerializer(serializers.Serializer):
    rsvp_status = serializers.ChoiceField(choices=['accepted', 'declined'])
    note = serializers.CharField(required=False, allow_blank=True)
