from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from apps.main.models import Post
from apps.comments.models import Comment
from apps.likes.models import Like
from django.contrib.auth import get_user_model


KARMA_RULES = {
    'post_created': 10,
    'post_deleted': -10,
    'comment_created': 5,
    'comment_deleted': -5,
    'like_received': 1,
    'like_removed': -1,
}

_deleting_users = set()


@receiver(pre_delete, sender=get_user_model())
def on_user_pre_delete(sender, instance, **kwargs):
    """Маркуємо юзера як такого що видаляється"""
    _deleting_users.add(instance.pk)


@receiver(post_delete, sender=get_user_model())
def on_user_post_delete(sender, instance, **kwargs):
    """Прибираємо маркер після видалення"""
    _deleting_users.discard(instance.pk)


def _safe_add_karma(user, points, reason):
    """Додає карму тільки якщо юзер не видаляється"""
    if user.pk in _deleting_users:
        return
    user.add_karma(points, reason)


@receiver(post_save, sender=Post)
def on_post_created(sender, instance, created, **kwargs):
    if created:
        _safe_add_karma(
            instance.author,
            KARMA_RULES['post_created'],
            f'Створено пост "{instance.title}"'
        )


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    _safe_add_karma(
        instance.author,
        KARMA_RULES['post_deleted'],
        f'Видалено пост "{instance.title}"'
    )


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance, created, **kwargs):
    if created:
        _safe_add_karma(
            instance.author,
            KARMA_RULES['comment_created'],
            f'Коментар до поста "{instance.post.title}"'
        )


@receiver(post_delete, sender=Comment)
def on_comment_deleted(sender, instance, **kwargs):
    _safe_add_karma(
        instance.author,
        KARMA_RULES['comment_deleted'],
        'Видалено коментар'
    )


@receiver(post_save, sender=Like)
def on_like_created(sender, instance, created, **kwargs):
    if created and hasattr(instance.content_object, 'author'):
        _safe_add_karma(
            instance.content_object.author,
            KARMA_RULES['like_received'],
            f'Лайк на "{instance.content_object}"'
        )


@receiver(post_delete, sender=Like)
def on_like_deleted(sender, instance, **kwargs):
    if hasattr(instance.content_object, 'author'):
        _safe_add_karma(
            instance.content_object.author,
            KARMA_RULES['like_removed'],
            'Видалено лайк'
        )
