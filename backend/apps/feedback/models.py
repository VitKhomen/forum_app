from django.db import models
from django.conf import settings


class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=300, verbose_name="Тема")
    message = models.TextField(verbose_name="Повідомлення")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        db_table = 'feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} від {self.email}"
