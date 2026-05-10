from django.urls import path
from . import views

urlpatterns = [
    # Sprints
    path('sprints/',                     views.sprint_list,     name='sprint-list'),
    path('sprints/<int:pk>/',            views.sprint_detail,   name='sprint-detail'),
    path('sprints/<int:pk>/activate/',   views.sprint_activate, name='sprint-activate'),
    path('sprints/<int:pk>/complete/',   views.sprint_complete, name='sprint-complete'),
    path('sprints/<int:pk>/tasks/',      views.sprint_tasks,    name='sprint-tasks'),

    # Tasks
    path('tasks/',                       views.task_list,       name='task-list'),
    path('tasks/my/',                    views.my_tasks,        name='my-tasks'),
    path('tasks/<int:pk>/',              views.task_detail,     name='task-detail'),
    path('tasks/<int:pk>/move/',         views.task_move,       name='task-move'),
]
