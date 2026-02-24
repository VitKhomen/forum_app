from django.db import models
from django.conf import settings


class WatchlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlist'
    )
    tmdb_id = models.IntegerField(db_index=True)
    media_type = models.CharField(
        max_length=10, default='movie')  # 'movie' | 'tv'
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True)
    # ← було created_at, views.py очікував added_at
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist'
        unique_together = ('user', 'tmdb_id', 'media_type')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} → {self.title}"

    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w342{self.poster_path}"
        return None


class FavoriteMovie(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_movies'
    )
    tmdb_id = models.IntegerField(db_index=True)
    media_type = models.CharField(max_length=10, default='movie')
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)  # ← теж added_at

    class Meta:
        db_table = 'favorite_movies'
        unique_together = ('user', 'tmdb_id', 'media_type')
        ordering = ['-added_at']

    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w342{self.poster_path}"
        return None


class MovieRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='movie_ratings'
    )
    tmdb_id = models.IntegerField(db_index=True)
    media_type = models.CharField(max_length=10, default='movie')
    title = models.CharField(max_length=200, blank=True)
    poster_path = models.CharField(max_length=200, blank=True)
    rating = models.PositiveSmallIntegerField()  # 1-10
    review = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movie_ratings'
        unique_together = ('user', 'tmdb_id', 'media_type')
        ordering = ['-added_at']

    @property
    def poster_url(self):
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w342{self.poster_path}"
        return None
