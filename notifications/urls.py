from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/unread-count/', views.notification_unread_count, name='notification-unread-count'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification-mark-all-read'),
    path('notifications/<int:pk>/', views.notification_detail, name='notification-detail'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification-mark-read'),
]
