from rest_framework import serializers
from .models import Bookmark
from apps.main.serializers import PostListSerializer


class BookmarkSerializer(serializers.ModelSerializer):
    post_detail = PostListSerializer(source='post', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'post', 'post_detail', 'created_at']
        read_only_fields = ['id', 'created_at']
