from django.urls import path
from . import views

urlpatterns = [
    # Job Postings
    path('jobs/',                       views.job_posting_list,   name='job-posting-list'),
    path('jobs/<int:pk>/',              views.job_posting_detail, name='job-posting-detail'),
    path('jobs/<int:pk>/close/',        views.job_posting_close,  name='job-posting-close'),

    # Applicants
    path('applicants/',                 views.applicant_list,     name='applicant-list'),
    path('applicants/<int:pk>/',        views.applicant_detail,   name='applicant-detail'),

    # Applications
    path('applications/',               views.application_list,    name='application-list'),
    path('applications/<int:pk>/',      views.application_detail,  name='application-detail'),
    path('applications/<int:pk>/advance/', views.application_advance, name='application-advance'),

    # Interviews
    path('interviews/',                 views.interview_list,     name='interview-list'),
    path('interviews/<int:pk>/',        views.interview_detail,   name='interview-detail'),
]
