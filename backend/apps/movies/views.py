# apps/movies/views.py
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .services.tmdb_client import tmdb
from .models import WatchlistItem, MovieRating, FavoriteMovie
from .serializers import WatchlistSerializer, MovieRatingSerializer, FavoriteMovieSerializer


# ─── TMDB proxy endpoints ─────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_search(request):
    """GET /api/v1/movies/search/?q=inception&page=1"""
    query = request.query_params.get('q', '').strip()
    page = request.query_params.get('page', 1)

    if not query:
        return Response({'error': 'Параметр q обов\'язковий'}, status=400)

    data = tmdb.search_movies(query, page=int(page))
    if data is None:
        return Response({'error': 'Помилка TMDB API'}, status=503)

    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_detail(request, movie_id):
    """GET /api/v1/movies/<id>/"""
    data = tmdb.get_movie(movie_id)
    if data is None:
        return Response({'error': 'Фільм не знайдено'}, status=404)

    # Додаємо стан юзера якщо авторизований
    user_state = {
        'in_watchlist': False,
        'is_favorite': False,
        'user_rating': None,
    }

    if request.user.is_authenticated:
        user_state['in_watchlist'] = WatchlistItem.objects.filter(
            user=request.user, tmdb_id=movie_id
        ).exists()
        user_state['is_favorite'] = FavoriteMovie.objects.filter(
            user=request.user, tmdb_id=movie_id
        ).exists()
        rating = MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id
        ).first()
        if rating:
            user_state['user_rating'] = rating.rating

    return Response({**data, 'user_state': user_state})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_trending(request):
    """GET /api/v1/movies/trending/?time_window=week"""
    time_window = request.query_params.get('time_window', 'week')
    data = tmdb.get_trending(time_window)
    if data is None:
        return Response({'error': 'Помилка TMDB API'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_list_by_category(request, category):
    """
    GET /api/v1/movies/popular/
    GET /api/v1/movies/top_rated/
    GET /api/v1/movies/upcoming/
    GET /api/v1/movies/now_playing/
    """
    page = int(request.query_params.get('page', 1))
    handlers = {
        'popular': tmdb.get_popular,
        'top_rated': tmdb.get_top_rated,
        'upcoming': tmdb.get_upcoming,
        'now_playing': tmdb.get_now_playing,
    }

    handler = handlers.get(category)
    if not handler:
        return Response({'error': 'Невірна категорія'}, status=400)

    data = handler(page=page)
    if data is None:
        return Response({'error': 'Помилка TMDB API'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_genres(request):
    """GET /api/v1/movies/genres/"""
    data = tmdb.get_genres()
    if data is None:
        return Response({'error': 'Помилка TMDB API'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_discover(request):
    """
    GET /api/v1/movies/discover/?with_genres=28&primary_release_year=2024&sort_by=popularity.desc
    """
    filters = {}
    allowed_params = [
        'with_genres', 'primary_release_year', 'vote_average.gte',
        'vote_average.lte', 'sort_by', 'page', 'with_original_language'
    ]
    for param in allowed_params:
        val = request.query_params.get(param)
        if val:
            filters[param] = val

    data = tmdb.discover_movies(**filters)
    if data is None:
        return Response({'error': 'Помилка TMDB API'}, status=503)
    return Response(data)


# ─── Юзерські endpoints ───────────────────────────────────────────────────────

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_watchlist(request, movie_id):
    """POST/DELETE /api/v1/movies/<id>/watchlist/"""
    item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        tmdb_id=movie_id,
        defaults=_get_movie_defaults(movie_id)
    )

    if not created:
        item.delete()
        return Response({'in_watchlist': False})

    return Response({'in_watchlist': True}, status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, movie_id):
    """POST/DELETE /api/v1/movies/<id>/favorite/"""
    item, created = FavoriteMovie.objects.get_or_create(
        user=request.user,
        tmdb_id=movie_id,
        defaults=_get_movie_defaults(movie_id)
    )

    if not created:
        item.delete()
        return Response({'is_favorite': False})

    return Response({'is_favorite': True}, status=status.HTTP_201_CREATED)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def movie_rating(request, movie_id):
    """POST/PUT/DELETE /api/v1/movies/<id>/rate/"""
    if request.method == 'DELETE':
        MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id).delete()
        return Response({'user_rating': None})

    serializer = MovieRatingSerializer(data={
        **request.data,
        'tmdb_id': movie_id,
    })
    serializer.is_valid(raise_exception=True)

    obj, created = MovieRating.objects.update_or_create(
        user=request.user,
        tmdb_id=movie_id,
        defaults={
            'rating': serializer.validated_data['rating'],
            'review': serializer.validated_data.get('review', ''),
            'title': serializer.validated_data.get('title', ''),
        }
    )
    return Response({'user_rating': obj.rating}, status=status.HTTP_201_CREATED if created else 200)


class MyWatchlistView(generics.ListAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user)


class MyFavoritesView(generics.ListAPIView):
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user)


# ─── Хелпер ──────────────────────────────────────────────────────────────────

def _get_movie_defaults(movie_id: int) -> dict:
    """Отримуємо базові дані фільму для збереження"""
    movie = tmdb.get_movie(movie_id)
    if movie:
        return {
            'title': movie.get('title', ''),
            'poster_path': movie.get('poster_path', ''),
        }
    return {'title': '', 'poster_path': ''}
