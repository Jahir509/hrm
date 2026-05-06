from django.urls import path
from . import views

urlpatterns = [
    path('departments/',     views.department_list,   name='department-list'),
    path('departments/<int:pk>/', views.department_detail, name='department-detail'),
    path('employees/',       views.employee_list,     name='employee-list'),
    path('employees/<int:pk>/',   views.employee_detail,  name='employee-detail'),
]
