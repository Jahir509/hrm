from django.urls import path
from . import views

urlpatterns = [
    path('attendance/',             views.attendance_list,    name='attendance-list'),
    path('attendance/my/',          views.my_attendance,      name='my-attendance'),
    path('attendance/check-in/',    views.attendance_check_in,  name='attendance-check-in'),
    path('attendance/check-out/',   views.attendance_check_out, name='attendance-check-out'),
    path('attendance/summary/',     views.attendance_summary,   name='attendance-summary'),
    path('attendance/today/',       views.attendance_today,     name='attendance-today'),
    path('attendance/<int:pk>/',    views.attendance_detail,  name='attendance-detail'),
]
