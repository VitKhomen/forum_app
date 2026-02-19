# apps/movies/serializers.py
from rest_framework import serializers
from .models import WatchlistItem, MovieRating, FavoriteMovie
from .services.tmdb_client import tmdb


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ['id', 'tmdb_id', 'title', 'poster_path', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_tmdb_id(self, value):
        # Перевіряємо чи існує фільм в TMDB
        movie = tmdb.get_movie(value)
        if not movie:
            raise serializers.ValidationError("Фільм не знайдено в TMDB")
        return value

    def create(self, validated_data):
        # Автоматично заповнюємо title і poster якщо не передані
        if not validated_data.get('title'):
            movie = tmdb.get_movie(validated_data['tmdb_id'])
            if movie:
                validated_data['title'] = movie.get('title', '')
                validated_data['poster_path'] = movie.get('poster_path', '')
        return super().create(validated_data)


class MovieRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieRating
        fields = ['id', 'tmdb_id', 'title', 'rating',
                  'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Оцінка має бути від 1 до 10")
        return value


class FavoriteMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteMovie
        fields = ['id', 'tmdb_id', 'title', 'poster_path', 'created_at']
        read_only_fields = ['id', 'created_at']
