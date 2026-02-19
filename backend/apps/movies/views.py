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
    q = request.query_params.get('q', '').strip()
    page = int(request.query_params.get('page', 1))
    media_type = request.query_params.get('media_type', 'movie')
    if media_type not in ('movie', 'tv'):
        media_type = 'movie'
    if not q:
        return Response({'error': "Параметр 'q' обов'язковий"}, status=400)
    data = tmdb.search(q, page=page, media_type=media_type)
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def movie_detail(request, movie_id):
    media_type = request.query_params.get('media_type', 'movie')
    data = tmdb.get_movie(
        movie_id) if media_type == 'movie' else tmdb.get_tv(movie_id)
    if data is None:
        return Response({'error': 'Не знайдено'}, status=404)

    user_state = {'in_watchlist': False,
                  'is_favorite': False, 'user_rating': None}
    if request.user.is_authenticated:
        user_state['in_watchlist'] = WatchlistItem.objects.filter(
            user=request.user, tmdb_id=movie_id).exists()
        user_state['is_favorite'] = FavoriteMovie.objects.filter(
            user=request.user, tmdb_id=movie_id).exists()
        rating = MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id).first()
        if rating:
            user_state['user_rating'] = rating.rating

    return Response({**data, 'user_state': user_state})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_trending(request):
    media_type = request.query_params.get('media_type', 'movie')
    time_window = request.query_params.get('time_window', 'week')
    if media_type not in ('movie', 'tv', 'all'):
        media_type = 'movie'
    data = tmdb.get_trending(media_type=media_type, time_window=time_window)
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_genres(request):
    media_type = request.query_params.get('media_type', 'movie')
    if media_type not in ('movie', 'tv'):
        media_type = 'movie'
    data = tmdb.get_genres(media_type=media_type)
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_discover(request):
    media_type = request.query_params.get('media_type', 'movie')
    if media_type not in ('movie', 'tv'):
        media_type = 'movie'

    allowed = [
        'with_genres', 'primary_release_year', 'first_air_date_year',
        'vote_average.gte', 'vote_average.lte', 'sort_by', 'page',
        'with_original_language',
    ]
    filters = {k: request.query_params[k]
               for k in allowed if k in request.query_params}

    data = tmdb.discover(media_type=media_type, **filters)
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_recommendations(request, movie_id):
    media_type = request.query_params.get('media_type', 'movie')
    data = tmdb.get_recommendations(movie_id, media_type=media_type)
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def movie_list_by_category(request, category):
    page = int(request.query_params.get('page', 1))
    media_type = request.query_params.get('media_type', 'movie')

    handlers = {
        'popular': lambda: tmdb.get_popular(page=page, media_type=media_type),
        'top_rated': lambda: tmdb.get_top_rated(page=page, media_type=media_type),
        'upcoming': lambda: tmdb.get_upcoming(page=page),
        'now_playing': lambda: tmdb.get_now_playing(page=page),
        'on_the_air': lambda: tmdb.get_on_the_air(page=page),
    }

    handler = handlers.get(category)
    if not handler:
        return Response({'error': f'Невідома категорія: {category}'}, status=400)

    data = handler()
    if data is None:
        return Response({'error': 'TMDB API недоступний'}, status=503)
    return Response(data)


# ─── Юзерські endpoints ────────────────────────────────────────────────────────

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_watchlist(request, movie_id):
    item, created = WatchlistItem.objects.get_or_create(
        user=request.user, tmdb_id=movie_id,
        defaults=_movie_defaults(movie_id)
    )
    if not created:
        item.delete()
        return Response({'in_watchlist': False})
    return Response({'in_watchlist': True}, status=201)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, movie_id):
    item, created = FavoriteMovie.objects.get_or_create(
        user=request.user, tmdb_id=movie_id,
        defaults=_movie_defaults(movie_id)
    )
    if not created:
        item.delete()
        return Response({'is_favorite': False})
    return Response({'is_favorite': True}, status=201)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def movie_rating(request, movie_id):
    if request.method == 'DELETE':
        MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id).delete()
        return Response({'user_rating': None})
    serializer = MovieRatingSerializer(
        data={**request.data, 'tmdb_id': movie_id})
    serializer.is_valid(raise_exception=True)
    obj, created = MovieRating.objects.update_or_create(
        user=request.user, tmdb_id=movie_id,
        defaults={
            'rating': serializer.validated_data['rating'],
            'review': serializer.validated_data.get('review', ''),
        }
    )
    return Response({'user_rating': obj.rating}, status=201 if created else 200)


class MyWatchlistView(generics.ListAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user).order_by('-added_at')


class MyFavoritesView(generics.ListAPIView):
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteMovie.objects.filter(user=self.request.user).order_by('-added_at')


def _movie_defaults(movie_id: int) -> dict:
    movie = tmdb.get_movie(movie_id)
    return {'title': movie.get('title', '') if movie else '', 'poster_path': movie.get('poster_path', '') if movie else ''}
