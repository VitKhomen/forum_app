# apps/karma/views.py — додай новий action my_karma_history

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from .models import KarmaHistory
from .serializers import KarmaHistorySerializer, UserKarmaSerializer

User = get_user_model()


class KarmaHistoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class KarmaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def my_karma(self, request):
        """Моя карма + остання історія"""
        serializer = UserKarmaSerializer(request.user)
        return Response(serializer.data)

    # ✅ НОВИЙ endpoint: пагінована історія
    @action(detail=False, methods=['get'], url_path='my_history')
    def my_history(self, request):
        """Пагінована історія карми поточного користувача"""
        queryset = KarmaHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')

        paginator = KarmaHistoryPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = KarmaHistorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def user_karma(self, request, username=None):
        """Карма конкретного користувача"""
        try:
            user = User.objects.get(username=username)
            serializer = UserKarmaSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)/history')
    def user_history(self, request, username=None):
        """Пагінована історія карми конкретного користувача"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        queryset = KarmaHistory.objects.filter(
            user=user
        ).order_by('-created_at')

        paginator = KarmaHistoryPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = KarmaHistorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Топ користувачів за кармою"""
        limit = int(request.query_params.get('page_size', 50))
        top_users = User.objects.order_by('-karma_points')[:limit]
        serializer = UserKarmaSerializer(top_users, many=True)
        return Response(serializer.data)
