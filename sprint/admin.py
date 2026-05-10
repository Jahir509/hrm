from django.contrib import admin
from .models import Sprint, Task


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'status', 'start_date', 'end_date', 'created_by')
    list_filter   = ('status',)
    search_fields = ('name', 'goal')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'sprint', 'assigned_to', 'status', 'priority', 'story_points', 'due_date')
    list_filter   = ('status', 'priority', 'sprint')
    search_fields = ('title', 'description', 'assigned_to__username')
    readonly_fields = ('created_at', 'updated_at')
