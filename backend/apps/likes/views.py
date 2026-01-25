from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from .models import Like
from apps.main.models import Post
from apps.comments.models import Comment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request):
    """
    Додати/видалити лайк для поста або коментаря

    Body: {
        "content_type": "post" or "comment",
        "object_id": 123
    }
    """
    content_type_name = request.data.get('content_type')
    object_id = request.data.get('object_id')

    if not content_type_name or not object_id:
        return Response(
            {'error': 'content_type та object_id обов\'язкові'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Визначаємо модель
    if content_type_name == 'post':
        model = Post
        obj = get_object_or_404(Post, id=object_id, status='published')
    elif content_type_name == 'comment':
        model = Comment
        obj = get_object_or_404(Comment, id=object_id, is_active=True)
    else:
        return Response(
            {'error': 'Невірний content_type. Використовуйте "post" або "comment"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    content_type = ContentType.objects.get_for_model(model)

    # Перевіряємо чи існує лайк
    like, created = Like.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=object_id
    )

    if created:
        # Лайк додано
        return Response({
            'liked': True,
            'likes_count': obj.likes_count,
            'message': 'Лайк додано'
        }, status=status.HTTP_201_CREATED)
    else:
        # Лайк вже існував - видаляємо
        like.delete()
        return Response({
            'liked': False,
            'likes_count': obj.likes_count,
            'message': 'Лайк видалено'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_likes_count(request):
    """
    Отримати кількість лайків для об'єкта

    Query params: ?content_type=post&object_id=123
    """
    content_type_name = request.query_params.get('content_type')
    object_id = request.query_params.get('object_id')

    if not content_type_name or not object_id:
        return Response(
            {'error': 'content_type та object_id обов\'язкові'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if content_type_name == 'post':
        model = Post
    elif content_type_name == 'comment':
        model = Comment
    else:
        return Response({'error': 'Невірний content_type'}, status=status.HTTP_400_BAD_REQUEST)

    content_type = ContentType.objects.get_for_model(model)
    likes_count = Like.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).count()

    # Перевірка чи користувач лайкнув
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).exists()

    return Response({
        'likes_count': likes_count,
        'is_liked': is_liked
    })
