from django.urls import path
from . import views
from .bootstrap import bootstrap_organization

urlpatterns = [
    # Organizations
    path('organizations/',                       views.organization_list,     name='organization-list'),
    path('organizations/bootstrap/',             bootstrap_organization,      name='organization-bootstrap'),
    path('organizations/primary/',               views.primary_organization,  name='organization-primary'),
    path('organizations/<int:pk>/',              views.organization_detail,   name='organization-detail'),
    path('organizations/<int:pk>/branches/',     views.organization_branches, name='organization-branches'),

    # Branches
    path('branches/',                            views.branch_list,           name='branch-list'),
    path('branches/<int:pk>/',                   views.branch_detail,         name='branch-detail'),

    # Holidays
    path('holidays/',                            views.holiday_list,          name='holiday-list'),
    path('holidays/<int:pk>/',                   views.holiday_detail,        name='holiday-detail'),

    # Work schedules
    path('work-schedules/',                      views.work_schedule_list,    name='work-schedule-list'),
    path('work-schedules/<int:pk>/',             views.work_schedule_detail,  name='work-schedule-detail'),

    # Documents
    path('organization-documents/',              views.document_list,         name='organization-document-list'),
    path('organization-documents/<int:pk>/',     views.document_detail,       name='organization-document-detail'),

    # Social links
    path('organization-social-links/',           views.social_link_list,      name='organization-social-link-list'),
    path('organization-social-links/<int:pk>/',  views.social_link_detail,    name='organization-social-link-detail'),
]
