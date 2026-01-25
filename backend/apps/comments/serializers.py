from rest_framework import serializers

from .models import Comment
from apps.main.models import Post


class CommentSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    replies_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'author_info', 'parent',
            'is_active', 'replies_count', 'is_reply',
            'created_at', 'updated_at', 'likes_count', 'is_liked',
        ]
        read_only_fields = ['author', 'is_active']

    def get_author_info(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'username': author.username,
            'full_name': author.full_name,
            'avatar': author.avatar.url if hasattr(author, 'avatar') and author.avatar else None,
        }

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['post', 'parent', 'content']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id, status='published').exists():
            raise serializers.ValidationError('Post not found')
        return value

    def validate(self, attrs):
        """Валідація після того як всі поля провалідовані"""
        parent = attrs.get('parent')
        post = attrs.get('post')

        if parent and parent.post != post:
            raise serializers.ValidationError({
                'parent': 'Parent comment must belong to the same post.'
            })

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError(
                "Тільки авторизовані користувачі можуть залишати коментарі"
            )

        validated_data['author'] = user
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):

    class Meta(CommentSerializer.Meta):
        model = Comment
        fields = ['content']


class CommentDetailSerializer(CommentSerializer):

    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = CommentSerializer.Meta.fields + ['replies']

    def get_replies(self, obj):
        if obj.parent is None:  # тільки для кореневих коментарів
            replies = obj.replies.filter(is_active=True).order_by('created_at')
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
