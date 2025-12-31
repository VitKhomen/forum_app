from django.urls import path
from .views import FeedbackView

urlpatterns = [
    path('send/', FeedbackView.as_view(), name='send-feedback'),
]
