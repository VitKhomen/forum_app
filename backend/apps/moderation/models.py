from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Report(models.Model):

    class Reason(models.TextChoices):
        SPAM = 'spam',        'Спам'
        HATE = 'hate',        'Ненависть / образи'
        MISLEADING = 'misleading',  'Дезінформація'
        NSFW = 'nsfw',        'Небажаний контент'
        OTHER = 'other',       'Інше'

    class Status(models.TextChoices):
        PENDING = 'pending',  'На розгляді'
        RESOLVED = 'resolved', 'Вирішено — видалено'
        REJECTED = 'rejected', 'Відхилено — залишено'

    # Хто поскаржився
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_sent'
    )

    # Generic FK — можна скаржитись на Post або Comment
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    reason = models.CharField(
        max_length=20, choices=Reason.choices, default=Reason.OTHER)
    comment = models.TextField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING)

    # Хто з адмінів розглянув і коли
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reports_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        # Один юзер — один репорт на один обʼєкт
        unique_together = ('reporter', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'Report #{self.pk} by {self.reporter.username} [{self.status}]'

    @property
    def content_type_name(self):
        """Повертає 'post' або 'comment' для фронтенду"""
        return self.content_type.model
