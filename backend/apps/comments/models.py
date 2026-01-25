from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings


class Comment(models.Model):
    post = models.ForeignKey(
        'main.Post', on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    content = models.TextField()
    likes = GenericRelation('likes.Like', related_query_name='comment')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def replies_count(self):
        return self.replies.filter(is_active=True).count()

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def post_title(self):
        return self.post.title

    @property
    def likes_count(self):
        """Кількість лайків"""
        return self.likes.count()

    def is_liked_by(self, user):
        """Чи лайкнув користувач цей коментар"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
