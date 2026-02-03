from django.db import models
from django.conf import settings


class KarmaHistory(models.Model):
    """Історія нарахувань карми (тільки для аудиту)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='karma_history'
    )
    points = models.IntegerField()  # +10, -5, +1, тощо
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Історія карми'
        verbose_name_plural = 'Історія карми'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        sign = '+' if self.points >= 0 else ''
        return f"{self.user.username}: {sign}{self.points} - {self.reason}"
