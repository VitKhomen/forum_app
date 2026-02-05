from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import KarmaHistory
from .serializers import KarmaHistorySerializer, UserKarmaSerializer

User = get_user_model()


class KarmaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_karma(self, request):
        """Моя карма + історія"""
        serializer = UserKarmaSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def user_karma(self, request, username=None):
        """Карма конкретного користувача"""
        try:
            user = User.objects.get(username=username)
            serializer = UserKarmaSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Топ користувачів за кармою"""
        limit = int(request.query_params.get('page_size', 50))
        top_users = User.objects.order_by('-karma_points')[:limit]
        serializer = UserKarmaSerializer(top_users, many=True)
        return Response(serializer.data)
