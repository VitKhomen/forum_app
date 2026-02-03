from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.main.models import Post
from apps.comments.models import Comment
from apps.likes.models import Like

KARMA_RULES = {
    'post_created': 10,
    'post_deleted': -10,
    'comment_created': 5,
    'comment_deleted': -5,
    'like_received': 1,
    'like_removed': -1,
}


@receiver(post_save, sender=Post)
def on_post_created(sender, instance, created, **kwargs):
    if created:
        instance.author.add_karma(
            KARMA_RULES['post_created'],
            f'Створено пост "{instance.title}"'
        )


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    instance.author.add_karma(
        KARMA_RULES['post_deleted'],
        f'Видалено пост "{instance.title}"'
    )


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance, created, **kwargs):
    if created:
        instance.author.add_karma(
            KARMA_RULES['comment_created'],
            f'Коментар до поста "{instance.post.title}"'
        )


@receiver(post_delete, sender=Comment)
def on_comment_deleted(sender, instance, **kwargs):
    instance.author.add_karma(
        KARMA_RULES['comment_deleted'],
        f'Видалено коментар'
    )


@receiver(post_save, sender=Like)
def on_like_created(sender, instance, created, **kwargs):
    if created and hasattr(instance.content_object, 'author'):
        instance.content_object.author.add_karma(
            KARMA_RULES['like_received'],
            f'Лайк на "{instance.content_object}"'
        )


@receiver(post_delete, sender=Like)
def on_like_deleted(sender, instance, **kwargs):
    if hasattr(instance.content_object, 'author'):
        instance.content_object.author.add_karma(
            KARMA_RULES['like_removed'],
            f'Видалено лайк'
        )
