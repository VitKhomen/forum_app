
from django.urls import path
from . import views

urlpatterns = [
    # Юзерські
    path('report/',  views.submit_report,  name='submit-report'),
    path('check/',   views.check_reported, name='check-reported'),

    # Адмін
    path('admin/queue/',               views.AdminReportQueueView.as_view(),
         name='admin-report-queue'),
    path('admin/stats/',               views.admin_stats,
         name='admin-stats'),
    path('admin/<int:report_id>/resolve/',
         views.resolve_report,             name='resolve-report'),
    path('admin/<int:report_id>/reject/',
         views.reject_report,              name='reject-report'),
]
