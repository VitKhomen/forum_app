from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    karma_points = models.IntegerField(default=0, db_index=True)
    karma_level = models.IntegerField(default=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def add_karma(self, points, reason=''):
        """Додати карму + зберегти в історію"""
        self.karma_points += points

        # Оновлюємо рівень (кожні 100 карми = +1 рівень)
        self.karma_level = 1 + (self.karma_points // 100)

        self.save(update_fields=['karma_points', 'karma_level'])

        # Зберігаємо в історію
        from apps.karma.models import KarmaHistory
        KarmaHistory.objects.create(
            user=self,
            points=points,
            reason=reason
        )

    def get_karma_history(self, limit=10):
        """Отримати останні N записів історії"""
        return self.karma_history.all().order_by('-created_at')[:limit]
