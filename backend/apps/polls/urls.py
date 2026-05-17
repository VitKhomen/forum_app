from django.urls import path
from . import views

urlpatterns = [
    path('', views.PollCreateView.as_view(), name='poll-create'),
    path('<int:poll_id>/vote/', views.PollVoteView.as_view(), name='poll-vote'),
]
