# apps/movies/models.py
from django.db import models
from django.conf import settings


class WatchlistItem(models.Model):
    """Фільми в списку перегляду юзера"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlist'
    )
    tmdb_id = models.IntegerField(db_index=True)
    # Кеш назви щоб не бити в API
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'tmdb_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.title}"


class MovieRating(models.Model):
    """Оцінки фільмів від юзерів"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='movie_ratings'
    )
    tmdb_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=200)
    rating = models.PositiveSmallIntegerField()   # 1-10
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movie_ratings'
        unique_together = ('user', 'tmdb_id')
        ordering = ['-created_at']


class FavoriteMovie(models.Model):
    """Улюблені фільми"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_movies'
    )
    tmdb_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorite_movies'
        unique_together = ('user', 'tmdb_id')
        ordering = ['-created_at']
