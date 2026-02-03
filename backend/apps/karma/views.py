from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserKarmaSerializer

User = get_user_model()


class KarmaViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_karma(self, request):
        """Моя карма + історія"""
        serializer = UserKarmaSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Топ-10 користувачів"""
        top_users = User.objects.order_by('-karma_points')[:10]
        serializer = UserKarmaSerializer(top_users, many=True)
        return Response(serializer.data)
