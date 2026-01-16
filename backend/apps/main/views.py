from django.db import transaction, models
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
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

# Pagination


class PopularPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

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
            return qs.filter(status='published')
        # Авторизовані бачать свої чернетки + всі опубліковані
        return qs.filter(Q(status='published') | Q(author=self.request.user))

    def get_serializer_class(self):
        """Різні серіалізатори для різних дій"""
        if self.action == 'list':
            return PostListSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostCreateUpdateSerializer

    def perform_create(self, serializer):
        """Додаємо автора при створенні"""
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Збільшуємо перегляди при отриманні поста"""
        instance = self.get_object()
        # Збільшуємо перегляди тільки для опублікованих і не від автора
        if instance.status == 'published' and instance.author != request.user:
            # Використовуємо F() для атомарного оновлення
            Post.objects.filter(pk=instance.pk).update(
                views_count=F('views_count') + 1)
            instance.views_count += 1  # оновлюємо локальний об'єкт
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """GET /api/posts/my/ — список тільки моїх постів"""
        posts = self.get_queryset().filter(author=request.user)

        # Підтримка пагінації
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
        tag_slug = request.query_params.get('tag')
        if not tag_slug:
            raise ValidationError({'tag': 'Параметр tag обов\'язковий'})
        posts = self.get_queryset().filter(
            tags__slug=tag_slug,
            status='published'
        ).distinct()

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(
            posts, many=True, context={'request': request})
        return Response(serializer.data)


# ========================
# Base Media ViewSet (для images і videos)
# ========================
class BasePostMediaViewSet(viewsets.ModelViewSet):
    """
    Базовий ViewSet для роботи з медіа (зображення/відео) постів.
    Дочірні класи тільки перевизначають атрибути.
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    # Ці атрибути ОБОВ'ЯЗКОВО перевизначаються в дочірніх класах
    file_field_name = None  # 'image' або 'video'
    # максимальна кількість (10 для images, 5 для videos)
    max_items = None
    max_file_size = None    # тільки для відео (у байтах)

    def get_post(self):
        """Отримати пост по slug з URL"""
        return get_object_or_404(
            Post.objects.select_related('author'),
            slug=self.kwargs['post_slug']
        )

    def get_queryset(self):
        """Медіа конкретного поста"""
        post = self.get_post()
        return self.queryset.filter(post=post)

    def perform_create(self, serializer):
        """
        Створення медіа з підтримкою множинного завантаження.
        POST /api/posts/{slug}/images/ або /videos/
        Body: image[] або video[] (multiple files)
        """
        post = self.get_post()

        # Перевірка прав
        if post.author != self.request.user:
            self.permission_denied(self.request)

        # Отримуємо файли
        files = self.request.FILES.getlist(self.file_field_name)
        if not files:
            raise ValidationError({
                self.file_field_name: f'Не надано файлів для завантаження'
            })

        # Перевірка ліміту кількості
        current_count = self.queryset.filter(post=post).count()
        if self.max_items and current_count + len(files) > self.max_items:
            raise ValidationError({
                self.file_field_name: f'Максимум {self.max_items} елементів на пост. Зараз: {current_count}'
            })

        # Перевірка розміру файлів (тільки для відео)
        if self.max_file_size:
            for f in files:
                if f.size > self.max_file_size:
                    max_mb = self.max_file_size // (1024 * 1024)
                    raise ValidationError({
                        self.file_field_name: f'Файл {f.name} завеликий (макс {max_mb}MB)'
                    })

        # Автоматичний порядок
        max_order = self.queryset.filter(post=post).aggregate(
            models.Max('order')
        )['order__max'] or 0

        # Bulk create для продуктивності
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
        """Перевизначаємо create для коректної відповіді після bulk_create"""
        self.perform_create(None)
        return Response(
            {
                'message': f'Файли успішно завантажено',
                'count': len(request.FILES.getlist(self.file_field_name))
            },
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        """Видалення з перевіркою прав"""
        if instance.post.author != self.request.user:
            self.permission_denied(self.request)
        instance.delete()

    @action(detail=False, methods=['patch'])
    def reorder(self, request, post_slug):
        """
        PATCH /api/posts/{slug}/images/reorder/ або /videos/reorder/
        Body: {"orders": {"1": 0, "3": 2, "5": 1}}
        де ключ - ID об'єкта, значення - новий order
        """
        post = self.get_post()
        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        orders = request.data.get('orders', {})
        if not orders:
            raise ValidationError({'orders': 'Не вказано нові порядки'})

        # Оновлюємо в транзакції
        with transaction.atomic():
            for obj_id, new_order in orders.items():
                self.queryset.filter(id=int(obj_id), post=post).update(
                    order=int(new_order))

        return Response({'message': 'Порядок успішно оновлено'})

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request, post_slug):
        """
        DELETE /api/posts/{slug}/images/bulk_delete/ або /videos/bulk_delete/
        Body: {"ids": [1, 2, 3]}
        """
        post = self.get_post()
        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        ids = request.data.get('ids', [])
        if not ids:
            raise ValidationError({'ids': 'Не вказано ID для видалення'})

        # Видаляємо в транзакції
        with transaction.atomic():
            deleted_count, _ = self.queryset.filter(
                id__in=ids,
                post=post
            ).delete()

        return Response({
            'message': f'Видалено {deleted_count} елементів'
        })


# ========================
# Images ViewSet
# ========================
class PostImagesViewSet(BasePostMediaViewSet):
    """ViewSet для зображень поста"""
    queryset = PostImages.objects.all().order_by('order')
    serializer_class = PostImageSerializer
    file_field_name = 'image'
    max_items = 10

# ========================
# Videos ViewSet
# ========================


class PostVideosViewSet(BasePostMediaViewSet):
    """ViewSet для відео поста"""
    queryset = PostVideo.objects.all().order_by('order')
    serializer_class = PostVideoSerializer
    file_field_name = 'video'
    max_items = 5
    max_file_size = 100 * 1024 * 1024  # 100 MB


# ========================
# Додаткові ендпоінти
# ========================
@api_view(['GET'])
@permission_classes([AllowAny])
def popular_posts(request):
    """
    GET /api/posts/popular/
    Популярні пости за кількістю переглядів з пагінацією, пошуком і фільтром по категорії
    """
    queryset = Post.objects.filter(status='published') \
                           .select_related('author', 'category') \
                           .prefetch_related('tags') \
                           .order_by('-views_count')

    # Фільтри та пошук (аналогічно PostViewSet)
    if 'search' in request.query_params:
        search = request.query_params['search']
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()

    if 'category__slug' in request.query_params:
        category_slug = request.query_params['category__slug']
        queryset = queryset.filter(category__slug=category_slug)

    # Пагінація
    paginator = PopularPagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = PostListSerializer(
        page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_posts(request):
    """
    GET /api/posts/trending/?limit=10&days=7
    Trending пости (нові з найбільшою кількістю переглядів)
    """
    from django.utils import timezone
    from datetime import timedelta

    limit = int(request.query_params.get('limit', 14))
    days = int(request.query_params.get('days', 14))
    date_from = timezone.now() - timedelta(days=days)

    posts = Post.objects.filter(
        status='published',
        published_at__gte=date_from
    ).select_related('author', 'category') \
     .order_by('-views_count')[:limit]
    serializer = PostListSerializer(
        posts, many=True, context={'request': request})
    return Response(serializer.data)
