import logging
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger('apps.moderation')


@receiver(pre_delete, sender='main.Post')
def close_comment_reports_on_post_delete(sender, instance, **kwargs):
    """
    При видаленні поста — закриваємо всі pending-репорти
    на коментарі цього поста, бо після видалення поста
    коментарі зникають каскадно і репорти стають "сиротами".
    """
    try:
        from .models import Report
        from apps.comments.models import Comment

        # Знаходимо всі коментарі цього поста
        comment_ids = list(
            instance.comments.values_list('id', flat=True)
        )

        if not comment_ids:
            return

        comment_ct = ContentType.objects.get_for_model(Comment)

        # Закриваємо pending репорти на ці коментарі
        updated = Report.objects.filter(
            content_type=comment_ct,
            object_id__in=comment_ids,
            status='pending'
        ).update(
            status='rejected',
            admin_note=f'Автоматично закрито — пост "{instance.title}" видалено'
        )

        if updated:
            logger.info(
                'Auto-closed %d comment reports after post "%s" (id=%s) was deleted',
                updated, instance.title, instance.pk
            )

    except Exception as e:
        # Не валимо видалення поста через помилку в сигналі
        logger.error('Error closing comment reports on post delete: %s', e)
