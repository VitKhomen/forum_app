from django.db import transaction, models
from django.db.models import Count, ExpressionWrapper, FloatField, F, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


from .models import Category, Post, PostImages, PostVideo
from .serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    PostImageSerializer,
    PostVideoSerializer,
)
from .permissions import IsAuthorOrReadOnly
from apps.core.throttling import PostCreateMinuteThrottle, PostCreateDayThrottle


# ========================
# Category ViewSet
# ========================
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    # Кешування списку
    def list(self, request, *args, **kwargs):
        cache_key = "categories:list"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Якщо в кеші немає — виконуємо звичайний запит
        response = super().list(request, *args, **kwargs)

        # Зберігаємо в кеш на 1 годину
        cache.set(cache_key, response.data, timeout=3600)

        return response

    # Очищення кешу при змінах
    def perform_create(self, serializer):
        serializer.save()
        cache.delete("categories:list")

    def perform_update(self, serializer):
        serializer.save()
        cache.delete("categories:list")

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("categories:list")


class PopularPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


# ========================
# Post ViewSet
# ========================
class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постів з повним CRUD функціоналом"""
    queryset = Post.objects.select_related('author', 'category') \
                           .prefetch_related('tags', 'images', 'videos')
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PopularPagination
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'author']
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'updated_at',
                       'published_at', 'views_count']
    ordering = ['-published_at', '-created_at']

    def get_queryset(self):
        """Фільтрація в залежності від користувача"""
        qs = super().get_queryset()

        if not self.request.user.is_authenticated:
            qs = qs.filter(status='published')
        else:
            qs = qs.filter(
                Q(status='published') | Q(
                    author=self.request.user, status='draft')
            )

        author_username = (
            self.request.query_params.get('author_username') or
            self.request.query_params.get('author__username')
        )
        if author_username:
            qs = qs.filter(author__username=author_username,
                           status='published')

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostCreateUpdateSerializer

    def list(self, request, *args, **kwargs):
        # Не кешуємо для авторизованих користувачів (чернетки) та при пошуку
        if request.user.is_authenticated or request.query_params.get('search'):
            return super().list(request, *args, **kwargs)

        cache_key = f"posts:list:{self._get_query_key(request)}"

        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)   # 10 хвилин
        return response

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs['slug']
        cache_key = f"post:detail:{slug}"

        cached = cache.get(cache_key)
        if cached is not None:
            # Оновлюємо лічильник переглядів
            if cached.get('status') == 'published':
                Post.objects.filter(slug=slug).update(
                    views_count=F('views_count') + 1)
            return Response(cached)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=1800)  # 30 хвилин
        return response

    def _get_query_key(self, request):
        """Генерує ключ для кешу списку"""
        params = sorted(
            (k, v) for k, v in request.query_params.items()
            if k not in ['page']
        )
        return ":".join(f"{k}={v}" for k, v in params) or "all"

    # ==================== ІНВАЛІДАЦІЯ ====================
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        self._clear_post_cache(post)

    def perform_update(self, serializer):
        post = serializer.save()
        self._clear_post_cache(post)

    def perform_destroy(self, instance):
        self._clear_post_cache(instance)
        instance.delete()

    def _clear_post_cache(self, post):
        """Очищення всіх пов'язаних кешів"""
        cache.delete(f"post:detail:{post.slug}")
        cache.delete_pattern("posts:list:*")        # Redis дозволяє це
        cache.delete_pattern("popular:*")
        cache.delete_pattern("trending:*")
        cache.delete_pattern("posts:by_tag:*")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """GET /api/posts/my/ — список тільки моїх постів (включно чернетки)"""
        # Для свого профілю — всі пости включно чернетки
        posts = Post.objects.select_related('author', 'category') \
                            .prefetch_related('tags', 'images', 'videos') \
                            .filter(author=request.user) \
                            .order_by('-created_at')

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(
            posts, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """GET /api/posts/by_tag/?tag=python"""
        tag_name = request.query_params.get('tag')
        if not tag_name:
            raise ValidationError({'tag': "Параметр tag обов'язковий"})

        # Нормалізуємо тег (на всяк випадок)
        tag_name = tag_name.strip().lower()

        cache_key = f"posts:by_tag:{tag_name}"

        # Кешуємо тільки для публічних запитів
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        posts = self.get_queryset().filter(
            tags__name__iexact=tag_name,
            status='published'
        ).distinct()

        page = self.paginate_queryset(posts)

        if page is not None:
            serializer = PostListSerializer(
                page, many=True, context={'request': request})
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = PostListSerializer(
                posts, many=True, context={'request': request})
            response_data = serializer.data

        # Зберігаємо в кеш на 15 хвилин
        cache.set(cache_key, response_data, timeout=900)

        return Response(response_data)

    def get_throttles(self):
        if self.action == 'create':
            return [PostCreateMinuteThrottle(), PostCreateDayThrottle()]
        return super().get_throttles()


# ========================
# Base Media ViewSet
# ========================
class BasePostMediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    file_field_name = None
    max_items = None
    max_file_size = None

    def get_post(self):
        return get_object_or_404(
            Post.objects.select_related('author'),
            slug=self.kwargs['post_slug']
        )

    def get_queryset(self):
        post = self.get_post()
        return self.queryset.filter(post=post)

    def perform_create(self, serializer):
        post = self.get_post()
        if post.author != self.request.user:
            self.permission_denied(self.request)

        files = self.request.FILES.getlist(self.file_field_name)
        if not files:
            raise ValidationError({
                self.file_field_name: 'Не надано файлів для завантаження'
            })

        current_count = self.queryset.filter(post=post).count()
        if self.max_items and current_count + len(files) > self.max_items:
            raise ValidationError({
                self.file_field_name: f'Максимум {self.max_items} елементів на пост. Зараз: {current_count}'
            })

        if self.max_file_size:
            for f in files:
                if f.size > self.max_file_size:
                    max_mb = self.max_file_size // (1024 * 1024)
                    raise ValidationError({
                        self.file_field_name: f'Файл {f.name} завеликий (макс {max_mb}MB)'
                    })

        max_order = self.queryset.filter(post=post).aggregate(
            models.Max('order')
        )['order__max'] or 0

        instances = []
        for idx, file in enumerate(files):
            instances.append(
                self.serializer_class.Meta.model(
                    post=post,
                    **{self.file_field_name: file},
                    order=max_order + idx + 1
                )
            )

        self.serializer_class.Meta.model.objects.bulk_create(instances)

    def create(self, request, *args, **kwargs):
        self.perform_create(None)
        return Response(
            {
                'message': 'Файли успішно завантажено',
                'count': len(request.FILES.getlist(self.file_field_name))
            },
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        if instance.post.author != self.request.user:
            self.permission_denied(self.request)
        instance.delete()

    @action(detail=False, methods=['patch'])
    def reorder(self, request, post_slug):
        post = self.get_post()
        if post.author != request.user:
            return Response({'error': 'Недостатньо прав'}, status=status.HTTP_403_FORBIDDEN)

        orders = request.data.get('orders', {})
        if not orders:
            raise ValidationError({'orders': 'Не вказано нові порядки'})

        with transaction.atomic():
            for obj_id, new_order in orders.items():
                self.queryset.filter(id=int(obj_id), post=post).update(
                    order=int(new_order))

        return Response({'message': 'Порядок успішно оновлено'})

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request, post_slug):
        post = self.get_post()
        if post.author != request.user:
            return Response({'error': 'Недостатньо прав'}, status=status.HTTP_403_FORBIDDEN)

        ids = request.data.get('ids', [])
        if not ids:
            raise ValidationError({'ids': 'Не вказано ID для видалення'})

        with transaction.atomic():
            items = self.queryset.filter(id__in=ids, post=post)
            count = items.count()
            for item in items:
                item.delete()

        return Response({'message': f'Видалено {count} елементів'})


class PostImagesViewSet(BasePostMediaViewSet):
    queryset = PostImages.objects.all().order_by('order')
    serializer_class = PostImageSerializer
    file_field_name = 'image'
    max_items = 20


class PostVideosViewSet(BasePostMediaViewSet):
    queryset = PostVideo.objects.all().order_by('order')
    serializer_class = PostVideoSerializer
    file_field_name = 'video'
    max_items = 5
    max_file_size = 100 * 1024 * 1024


# ========================
# Додаткові ендпоінти
# ========================
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_posts(request):
    sort = request.query_params.get('sort', 'hot')
    search = request.query_params.get('search', '')
    cat = request.query_params.get('category__slug', '')
    limit = request.query_params.get('limit', '')
    offset = request.query_params.get('offset', '0')

    # Не кешуємо якщо є пошук
    use_cache = not search
    cache_key = f"popular:{sort}:{cat}:{limit}:{offset}"

    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

    queryset = Post.objects.filter(status='published') \
        .select_related('author', 'category') \
        .prefetch_related('tags') \
        .annotate(
            likes_count_ann=Count('likes', distinct=True),
            comments_count_ann=Count('comments', distinct=True),
    )

    if sort == 'hot':
        queryset = queryset.annotate(
            hot_score=ExpressionWrapper(
                Cast(F('views_count'), FloatField()) * 0.45
                + Cast(F('likes_count_ann'), FloatField()) * 2.8
                + Cast(F('comments_count_ann'), FloatField()) * 4.2,
                output_field=FloatField()
            )
        ).order_by('-hot_score')
    elif sort == 'views':
        queryset = queryset.order_by('-views_count')
    elif sort == 'likes':
        queryset = queryset.order_by('-likes_count_ann')
    elif sort == 'comments':
        queryset = queryset.order_by('-comments_count_ann')
    else:
        queryset = queryset.order_by('-views_count')

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()

    if cat:
        queryset = queryset.filter(category__slug=cat)

    paginator = LimitOffsetPagination()
    paginator.default_limit = 20
    paginator.max_limit = 100

    page = paginator.paginate_queryset(queryset, request)
    serializer = PostListSerializer(
        page, many=True, context={'request': request})
    response_data = paginator.get_paginated_response(serializer.data).data

    if use_cache:
        cache.set(cache_key, response_data, timeout=300)  # 5 хвилин

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_posts(request):
    from django.utils import timezone
    from datetime import timedelta

    days = int(request.query_params.get('days', 180))
    limit = int(request.query_params.get('limit', 30))
    cat = request.query_params.get('category__slug', '')

    cache_key = f"trending:{days}:{limit}:{cat}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    date_from = timezone.now() - timedelta(days=days)

    posts = Post.objects.filter(
        status='published',
        published_at__gte=date_from
    ).select_related('author', 'category') \
     .prefetch_related('tags') \
     .annotate(
         likes_count_ann=Count('likes', distinct=True),
         comments_count_ann=Count('comments', distinct=True),
         hot_score=ExpressionWrapper(
             Cast(F('views_count'), FloatField()) * 0.45
             + Cast(F('likes_count_ann'), FloatField()) * 2.8
             + Cast(F('comments_count_ann'), FloatField()) * 4.2,
             output_field=FloatField()
         )
    ).order_by('-hot_score')

    if cat:
        posts = posts.filter(category__slug=cat)

    posts = posts[:limit]

    serializer = PostListSerializer(
        posts, many=True, context={'request': request})
    cache.set(cache_key, serializer.data, timeout=600)  # 10 хвилин
    return Response(serializer.data)
