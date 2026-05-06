from django.urls import path
from . import views

urlpatterns = [
    # Leave Types
    path('leave-types/',          views.leave_type_list,   name='leave-type-list'),
    path('leave-types/<int:pk>/', views.leave_type_detail, name='leave-type-detail'),

    # Leave Balances
    path('leave-balances/',          views.leave_balance_list,   name='leave-balance-list'),
    path('leave-balances/<int:pk>/', views.leave_balance_detail, name='leave-balance-detail'),

    # Leave Requests
    path('leave-requests/',                       views.leave_request_list,   name='leave-request-list'),
    path('leave-requests/my/',                    views.my_leave_requests,    name='leave-request-my'),
    path('leave-requests/<int:pk>/',              views.leave_request_detail, name='leave-request-detail'),
    path('leave-requests/<int:pk>/review/',       views.leave_request_review, name='leave-request-review'),
    path('leave-requests/<int:pk>/cancel/',       views.leave_request_cancel, name='leave-request-cancel'),

    # Public Holidays
    path('public-holidays/',          views.public_holiday_list,   name='public-holiday-list'),
    path('public-holidays/<int:pk>/', views.public_holiday_detail, name='public-holiday-detail'),
]
