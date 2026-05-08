from django.urls import path
from . import views

urlpatterns = [
    # Events
    path('events/',          views.event_list,   name='event-list'),
    path('events/<int:pk>/', views.event_detail, name='event-detail'),

    # Attendees (nested under event)
    path('events/<int:pk>/attendees/',                    views.event_attendee_list,   name='event-attendee-list'),
    path('events/<int:pk>/attendees/<int:att_pk>/',       views.event_attendee_detail, name='event-attendee-detail'),

    # RSVP
    path('events/<int:pk>/rsvp/', views.event_rsvp, name='event-rsvp'),

    # Personal views
    path('my-events/',   views.my_events,   name='my-events'),
    path('my-calendar/', views.my_calendar, name='my-calendar'),
]
