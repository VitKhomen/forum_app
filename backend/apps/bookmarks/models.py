from django.db import models
from django.conf import settings


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    post = models.ForeignKey(
        'main.Post',
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'
        unique_together = ('user', 'post')  # не можна двічі зберегти
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.post.title}"
