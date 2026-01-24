from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Like(models.Model):
    """
    Універсальна модель для лайків будь-якого контенту
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    # GenericForeignKey дозволяє лайкати різні моделі (Post, Comment, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        # Один користувач може лайкнути конкретний об'єкт тільки 1 раз
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.content_object}"
