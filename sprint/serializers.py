from rest_framework import serializers
from .models import Sprint, Task


class SprintSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    task_count      = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model  = Sprint
        fields = [
            'id',
            'name',
            'goal',
            'start_date',
            'end_date',
            'status',
            'created_by',
            'created_by_name',
            'task_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate(self, data):
        start = data.get('start_date', getattr(self.instance, 'start_date', None))
        end   = data.get('end_date',   getattr(self.instance, 'end_date',   None))
        if start and end and end <= start:
            raise serializers.ValidationError({'end_date': 'End date must be after start date.'})
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name  = serializers.CharField(source='created_by.get_full_name',  read_only=True)
    sprint_name      = serializers.CharField(source='sprint.name', read_only=True)

    class Meta:
        model  = Task
        fields = [
            'id',
            'sprint',
            'sprint_name',
            'title',
            'description',
            'assigned_to',
            'assigned_to_name',
            'created_by',
            'created_by_name',
            'status',
            'priority',
            'story_points',
            'due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value

    def validate(self, data):
        sprint   = data.get('sprint',   getattr(self.instance, 'sprint',   None))
        due_date = data.get('due_date', getattr(self.instance, 'due_date', None))
        if sprint and due_date and due_date > sprint.end_date:
            raise serializers.ValidationError(
                {'due_date': 'Task due date cannot be after the sprint end date.'}
            )
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
