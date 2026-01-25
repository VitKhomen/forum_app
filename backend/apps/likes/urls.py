from django.urls import path
from . import views

urlpatterns = [
    path('toggle/', views.toggle_like, name='toggle-like'),
    path('count/', views.get_likes_count, name='likes-count'),
]
