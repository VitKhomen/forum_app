from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import KarmaHistory

User = get_user_model()


class KarmaHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = KarmaHistory
        fields = ['points', 'reason', 'created_at']


class UserKarmaSerializer(serializers.ModelSerializer):
    recent_history = serializers.SerializerMethodField()
    posts_created = serializers.SerializerMethodField()
    comments_created = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'karma_points', 'karma_level',
                  'posts_created', 'comments_created', 'recent_history']

    def get_recent_history(self, obj):
        history = obj.get_karma_history(10)
        return KarmaHistorySerializer(history, many=True).data

    def get_posts_created(self, obj):
        try:
            return obj.posts.count()
        except:
            return 0

    def get_comments_created(self, obj):
        try:
            return obj.comments.count()
        except:
            return 0
