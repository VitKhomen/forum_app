from rest_framework import serializers
from .models import WatchlistItem, MovieRating, FavoriteMovie


class WatchlistSerializer(serializers.ModelSerializer):
    poster_url = serializers.ReadOnlyField()

    class Meta:
        model = WatchlistItem
        fields = ['id', 'tmdb_id', 'media_type', 'title',
                  'poster_path', 'poster_url', 'added_at']
        read_only_fields = ['id', 'added_at', 'poster_url']


class FavoriteMovieSerializer(serializers.ModelSerializer):
    poster_url = serializers.ReadOnlyField()

    class Meta:
        model = FavoriteMovie
        fields = ['id', 'tmdb_id', 'media_type', 'title',
                  'poster_path', 'poster_url', 'added_at']
        read_only_fields = ['id', 'added_at', 'poster_url']


class MovieRatingSerializer(serializers.ModelSerializer):
    poster_url = serializers.ReadOnlyField()

    class Meta:
        model = MovieRating
        fields = ['id', 'tmdb_id', 'media_type', 'title', 'poster_path', 'poster_url',
                  'rating', 'review', 'added_at', 'updated_at']
        read_only_fields = ['id', 'added_at', 'updated_at',
                            'poster_url', 'tmdb_id', 'title', 'poster_path']

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Оцінка має бути від 1 до 10")
        return value
