from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KarmaViewSet

router = DefaultRouter()
router.register('karma', KarmaViewSet, basename='karma')

urlpatterns = [
    path('', include(router.urls)),
]
