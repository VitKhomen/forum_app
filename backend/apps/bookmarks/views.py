from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Bookmark
from .serializers import BookmarkSerializer
from apps.main.models import Post
from apps.core.throttling import BookmarkThrottle


class BookmarkPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class MyBookmarksView(generics.ListAPIView):
    """GET /api/v1/bookmarks/ — список моїх закладок"""
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BookmarkPagination

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related('post', 'post__author', 'post__category')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request, post_id):
    """
    POST /api/v1/bookmarks/<post_id>/toggle/
    Додає або видаляє закладку
    """

    throttles = [BookmarkThrottle()]
    for throttle in throttles:
        if not throttle.allow_request(request, None):
            from rest_framework.exceptions import Throttled
            raise Throttled(detail='Забагато запитів до закладок.')

    post = get_object_or_404(Post, id=post_id, status='published')

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        post=post
    )

    if created:
        return Response({
            'bookmarked': True,
            'message': 'Додано до закладок'
        }, status=status.HTTP_201_CREATED)
    else:
        bookmark.delete()
        return Response({
            'bookmarked': False,
            'message': 'Видалено із закладок'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_bookmark(request, post_id):
    """
    GET /api/v1/bookmarks/<post_id>/check/
    Перевіряє чи пост є в закладках
    """
    is_bookmarked = Bookmark.objects.filter(
        user=request.user,
        post_id=post_id
    ).exists()

    return Response({'bookmarked': is_bookmarked})
