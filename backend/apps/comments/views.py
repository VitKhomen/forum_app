from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core.cache import cache

from .models import Comment
from .serializers import CommentSerializer, CommentDetailSerializer, \
    CommentCreateSerializer, CommentUpdateSerializer
from .permissions import IsAuthorOrReadOnly
from apps.main.models import Post


class CommentPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CommentPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'parent']
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Comment.objects.filter(is_active=True).select_related(
            'author', 'post', 'parent'
        ).prefetch_related(
            Prefetch(
                'replies',
                queryset=Comment.objects.filter(
                    is_active=True).select_related('author')
            )
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CommentCreateSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Скидаємо кеш коментарів цього поста
        _invalidate_comments_cache(comment.post_id)

        full_serializer = CommentSerializer(
            comment, context={'request': request})
        return Response(full_serializer.data, status=201)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter(is_active=True).select_related(
        'author', 'post'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Comment.objects.filter(
                is_active=True).select_related('author')
        )
    )
    serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def update(self, request, *args, **kwargs):
        """Перевизначаємо update щоб повертати повний серіалізований об'єкт"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Використовуємо CommentUpdateSerializer для валідації та збереження
        serializer = CommentUpdateSerializer(
            instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Скидаємо кеш
        _invalidate_comments_cache(comment.post_id)

        # Повертаємо повний об'єкт через CommentDetailSerializer
        full_serializer = CommentDetailSerializer(
            comment, context={'request': request})
        return Response(full_serializer.data)

    def perform_destroy(self, instance):
        post_id = instance.post_id
        instance.is_active = False
        instance.save()
        _invalidate_comments_cache(post_id)


def _invalidate_comments_cache(post_id):
    """очищення кешу коментарів поста"""
    cache.delete_pattern(f"comments:post:{post_id}:*")


class MyCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'parent', 'is_active']
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Comment.objects.filter(
            author=self.request.user
        ).select_related('post', 'parent').prefetch_related(
            Prefetch(
                'replies',
                queryset=Comment.objects.filter(
                    is_active=True).select_related('author')
            )
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')

    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))

    # Кешуємо тільки першу сторінку анонімних запитів
    # Авторизовані — не кешуємо бо є is_liked який відрізняється
    use_cache = not request.user.is_authenticated
    cache_key = f"comments:post:{post_id}:limit:{limit}:offset:{offset}"

    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

    comments = Comment.objects.filter(
        post=post,
        is_active=True
    ).select_related('author').order_by('created_at')

    # Пагінація
    paginator = LimitOffsetPagination()
    paginator.default_limit = 20
    paginator.max_limit = 100

    page = paginator.paginate_queryset(comments, request)
    serializer = CommentSerializer(
        page, many=True, context={'request': request})

    response = paginator.get_paginated_response(serializer.data)
    response.data['post'] = {
        'id':    post.id,
        'title': post.title,
        'slug':  post.slug,
    }

    if use_cache:
        cache.set(cache_key, response.data, timeout=120)

    return response


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def comment_replies(request, comment_id):
    """Залишаємо для сумісності, але post_comments тепер повертає все"""
    parent_comment = get_object_or_404(Comment, id=comment_id, is_active=True)
    replies = Comment.objects.filter(
        parent=parent_comment, is_active=True
    ).select_related('author').order_by('created_at')
    serializer = CommentSerializer(
        replies, many=True, context={'request': request})
    return Response({
        'parent_comment': CommentSerializer(parent_comment, context={'request': request}).data,
        'replies': serializer.data,
        'total_replies': replies.count(),
    })
