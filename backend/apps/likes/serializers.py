from rest_framework import serializers

from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ['id', 'user', 'user_info', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar': obj.user.avatar.url if obj.user.avatar else None
        }
