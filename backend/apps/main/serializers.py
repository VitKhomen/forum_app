from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.utils.text import Truncator

from .models import Category, Post, PostImages, PostVideo


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description',
                  'posts_count', 'created_at']
        read_only_fields = ['slug', 'created_at', 'posts_count']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = ['id', 'image', 'order']  # image буде URL після серіалізації
        read_only_fields = ['id']


class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['id', 'video', 'order']  # video буде URL
        read_only_fields = ['id']


class PostListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка постов"""
    author_username = serializers.CharField(
        source='author.username', read_only=True)
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    images_count = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'image',
            'category', 'category_name',
            'author', 'author_username',
            'status', 'tags',
            'created_at', 'updated_at', 'published_at',
            'views_count', 'comments_count', 'images_count',
            'likes_count', 'is_liked',
        ]
        read_only_fields = ['slug', 'author', 'views_count', 'published_at']

    def get_excerpt(self, obj):
        """Скорочений текст для списку"""
        return Truncator(obj.content).chars(200, truncate='...')

    def get_images_count(self, obj):
        return obj.images.count()

    def get_comments_count(self, obj):
        """Кількість коментарів (якщо є модель Comment)"""
        if hasattr(obj, 'comments'):
            return obj.comments.count()
        return 0

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для списка постов"""
    author_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    tags = TagListSerializerField()
    images = PostImageSerializer(many=True, read_only=True)
    videos = PostVideoSerializer(many=True, read_only=True)
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'image',
            'category', 'category_info',
            'author', 'author_info',
            'status', 'tags',
            'created_at', 'updated_at', 'published_at',
            'views_count', 'comments_count',
            'images', 'videos', 'likes_count', 'is_liked'
        ]
        read_only_fields = ['slug', 'author', 'views_count', 'published_at']

    def get_author_info(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'username': author.username,
            'fullname': getattr(author, 'full_name', ''),
            'avatar': author.avatar.url if hasattr(author, 'avatar') and author.avatar else None,
        }

    def get_category_info(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'slug': obj.category.slug,
            }
        return None

    def get_comments_count(self, obj):
        if hasattr(obj, 'comments'):
            return obj.comments.count()
        return 0

    def get_is_liked(self, obj):
        """Перевірка чи поточний користувач лайкнув пост"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class PostCreateUpdateSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Використовується для створення та оновлення постів.
    Завантаження додаткових зображень та відео робиться у view через request.FILES:
        - images: список файлів (key='images')
        - videos: список файлів (key='videos')
    """
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Post
        fields = [
            'title',
            'slug',
            'content',
            'image',      # основне зображення поста
            'category',
            'status',
            'tags',
        ]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Заголовок повинен містити принаймні 5 символів"
            )
        return value

    def validate_content(self, value):
        if len(value) < 50:
            raise serializers.ValidationError(
                "Контент повинен містити принаймні 50 символів"
            )
        return value

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance
