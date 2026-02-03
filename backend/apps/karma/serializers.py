from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import KarmaHistory

User = get_user_model()


class KarmaHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KarmaHistory
        fields = ['points', 'reason', 'created_at']


class UserKarmaSerializer(serializers.ModelSerializer):
    recent_history = KarmaHistorySerializer(
        source='get_karma_history',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'karma_points', 'karma_level', 'recent_history']
