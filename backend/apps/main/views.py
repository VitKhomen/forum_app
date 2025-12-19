from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Max
from django.db import transaction, models
from django.shortcuts import get_object_or_404

from .models import Category, Post, PostImages, PostVideo
from .serializer import (CategorySerializer, PostListSerializer,
                         PostDetailSerializer, PostCreateUpdateSerializer,
                         PostImageSerializer, PostVideoSerializer)
from .permissions import IsAuthorOrReadOnly


class CategoryListCreateView(generics.ListCreateAPIView):
    """Список та створення категорій"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Деталі, оновлення та видалення категорії"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class PostListCreateView(generics.ListCreateAPIView):
    """Список постів та створення нового поста"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content', 'author_username', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-published_at', '-created_at']

    def get_queryset(self):
        """Фільтрація постів в залежності від юзера"""
        qs = Post.objects.select_related(
            'author', 'category').prefetch_related('tags')

        # Якщо не авторизований - тільки опубліковані
        if not self.request.user.is_authenticated:
            return qs.filter(status='published')

        # Якщо авторизований - опубліковані + свої чернетки
        return qs.filter(
            Q(status='published') | Q(author=self.request.user)
        )

    def get_serializer_class(self):
        """Різні серіалізатори для різних дій"""
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        """Додаємо автора при створенні"""
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Деталі поста, оновлення та видалення"""
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Оптимізований queryset з prefetch"""
        return Post.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'tags', 'images', 'videos'
        )

    def get_serializer_class(self):
        """Різні серіалізатори для різних методів"""
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if (instance.status == 'published' and
                instance.author != request.user):
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyPostsView(generics.ListAPIView):
    """Мої пости (для авторизованого користувача)"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Тільки пости поточного користувача"""
        return Post.objects.filter(
            author=self.request.user
        ).select_related('author', 'category').prefetch_related('tags')


class PostsByTagView(generics.ListAPIView):
    """Пости за тегом"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        return Post.objects.filter(
            tags__slug=tag_slug,
            status='published'
        ).select_related('author', 'category').distinct()


class PostsByCategoryView(generics.ListAPIView):
    """Пости за категорією"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return Post.objects.filter(
            category__slug=category_slug,
            status='published'
        ).select_related('author', 'category')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    """Популярні пости (топ за переглядами)"""
    limit = int(request.GET.get('limit', 10))

    posts = Post.objects.filter(
        status='published'
    ).select_related(
        'author', 'category'
    ).order_by('-views_count')[:limit]

    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_posts(request):
    """Trending пости (нові з найбільшою кількістю переглядів)"""
    from django.utils import timezone
    from datetime import timedelta

    limit = int(request.GET.get('limit', 10))
    days = int(request.GET.get('days', 7))

    date_from = timezone.now() - timedelta(days=days)

    posts = Post.objects.filter(
        status='published',
        published_at__gte=date_from
    ).select_related(
        'author', 'category'
    ).order_by('-views_count')[:limit]

    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)


# ============================================
# РОБОТА З ЗОБРАЖЕННЯМИ
# ============================================

class PostImagesAddView(APIView):
    """Додавання зображень до поста"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, slug):
        """
        POST /api/posts/{slug}/images/add/
        Body: images (multiple files), orders (optional)
        """
        post = get_object_or_404(
            Post.objects.select_related('author'),
            slug=slug
        )

        # Перевірка прав
        if post.author != request.user:
            return Response(
                {'error': 'Ви можете додавати зображення тільки до своїх постів'},
                status=status.HTTP_403_FORBIDDEN
            )

        images = request.FILES.getlist('images')
        orders = request.data.getlist('orders', [])

        if not images:
            return Response(
                {'error': 'Не надано жодного зображення'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ліміт зображень
        MAX_IMAGES = 10
        current_count = post.images.count()
        if current_count + len(images) > MAX_IMAGES:
            return Response(
                {'error': f'Максимум {MAX_IMAGES} зображень на пост. Зараз: {current_count}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                created_images = []
                max_order = post.images.aggregate(
                    Max('order'))['order__max'] or -1

                for idx, image in enumerate(images):
                    order = int(orders[idx]) if idx < len(
                        orders) else max_order + idx + 1

                    post_image = PostImages.objects.create(
                        post=post,
                        image=image,
                        order=order
                    )
                    created_images.append(post_image)

                serializer = PostImageSerializer(created_images, many=True)
                return Response(
                    {
                        'message': f'Додано {len(created_images)} зображень',
                        'images': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {'error': f'Помилка при завантаженні: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PostImageDetailView(APIView):
    """Видалення окремого зображення"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug, image_id):
        """
        DELETE /api/posts/{slug}/images/{image_id}/
        """
        post = get_object_or_404(Post, slug=slug)

        # Перевірка прав
        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            image = PostImages.objects.get(id=image_id, post=post)
            image.delete()

            return Response(
                {'message': 'Зображення видалено'},
                status=status.HTTP_204_NO_CONTENT
            )

        except PostImages.DoesNotExist:
            return Response(
                {'error': 'Зображення не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )


class PostImagesBulkDeleteView(APIView):
    """Масове видалення зображень"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug):
        """
        DELETE /api/posts/{slug}/images/bulk-delete/
        Body: {"image_ids": [1, 2, 3]}
        """
        post = get_object_or_404(Post, slug=slug)

        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        image_ids = request.data.get('image_ids', [])

        if not image_ids:
            return Response(
                {'error': 'Не надано ID зображень'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                deleted_count, _ = PostImages.objects.filter(
                    id__in=image_ids,
                    post=post
                ).delete()

                return Response(
                    {'message': f'Видалено {deleted_count} зображень'},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PostImagesReorderView(APIView):
    """Зміна порядку зображень"""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, slug):
        """
        PATCH /api/posts/{slug}/images/reorder/
        Body: {"orders": {"1": 0, "2": 1, "3": 2}}
        """
        post = get_object_or_404(Post, slug=slug)

        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        orders = request.data.get('orders', {})

        if not orders:
            return Response(
                {'error': 'Не надано порядку зображень'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                for image_id, new_order in orders.items():
                    PostImages.objects.filter(
                        id=int(image_id),
                        post=post
                    ).update(order=int(new_order))

                return Response(
                    {'message': 'Порядок оновлено'},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================
# РОБОТА З ВІДЕО
# ============================================

class PostVideosAddView(APIView):
    """Додавання відео до поста"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, slug):
        """
        POST /api/posts/{slug}/videos/add/
        Body: videos (multiple files), orders (optional)
        """
        post = get_object_or_404(Post, slug=slug)

        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        videos = request.FILES.getlist('videos')
        orders = request.data.getlist('orders', [])

        if not videos:
            return Response(
                {'error': 'Не надано жодного відео'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ліміти
        MAX_VIDEOS = 5
        MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

        current_count = post.videos.count()
        if current_count + len(videos) > MAX_VIDEOS:
            return Response(
                {'error': f'Максимум {MAX_VIDEOS} відео на пост. Зараз: {current_count}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                created_videos = []
                max_order = post.videos.aggregate(
                    Max('order'))['order__max'] or -1

                for idx, video in enumerate(videos):
                    # Перевірка розміру
                    if video.size > MAX_VIDEO_SIZE:
                        return Response(
                            {'error': f'Відео {video.name} завелике (макс 100MB)'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    order = int(orders[idx]) if idx < len(
                        orders) else max_order + idx + 1

                    post_video = PostVideo.objects.create(
                        post=post,
                        video=video,
                        order=order
                    )
                    created_videos.append(post_video)

                serializer = PostVideoSerializer(created_videos, many=True)
                return Response(
                    {
                        'message': f'Додано {len(created_videos)} відео',
                        'videos': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {'error': f'Помилка при завантаженні: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PostVideoDetailView(APIView):
    """Видалення окремого відео"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug, video_id):
        """
        DELETE /api/posts/{slug}/videos/{video_id}/
        """
        post = get_object_or_404(Post, slug=slug)

        if post.author != request.user:
            return Response(
                {'error': 'Недостатньо прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            video = PostVideo.objects.get(id=video_id, post=post)
            video.delete()

            return Response(
                {'message': 'Відео видалено'},
                status=status.HTTP_204_NO_CONTENT
            )

        except PostVideo.DoesNotExist:
            return Response(
                {'error': 'Відео не знайдено'},
                status=status.HTTP_404_NOT_FOUND
            )
