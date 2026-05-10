from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'recipient_name',
            'title',
            'message',
            'notification_type',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = ['is_read', 'read_at', 'created_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError('Message cannot be blank.')
        return value
