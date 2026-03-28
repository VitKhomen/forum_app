from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyBookmarksView.as_view(), name='my-bookmarks'),
    path('<int:post_id>/toggle/', views.toggle_bookmark, name='toggle-bookmark'),
    path('<int:post_id>/check/', views.check_bookmark, name='check-bookmark'),
]
