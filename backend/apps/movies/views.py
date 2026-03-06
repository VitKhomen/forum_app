from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .services.tmdb_client import tmdb
from .models import WatchlistItem, MovieRating, FavoriteMovie
from .serializers import WatchlistSerializer, MovieRatingSerializer, FavoriteMovieSerializer

User = get_user_model()


# ─── Хелпер: отримати дані фільму/серіалу з TMDB ─────────────────────────────
def _fetch_item_data(tmdb_id: int, media_type: str = 'movie') -> dict:
    """Отримує title і poster_path з TMDB. Гарантує що poster_path ніколи не None."""
    try:
        if media_type == 'tv':
            data = tmdb.get_tv(tmdb_id)
            return {
                'title': (data.get('name') or '') if data else '',
                'poster_path': (data.get('poster_path') or '') if data else '',
            }
        data = tmdb.get_movie(tmdb_id)
        return {
            'title': (data.get('title') or '') if data else '',
            'poster_path': (data.get('poster_path') or '') if data else '',
        }
    except Exception:
        return {'title': '', 'poster_path': ''}


# ═══════════════════════════════════════════════════════════════════════════════
# TMDB PROXY — фільми і серіали
# ═══════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def multi_search(request):
    """
    GET /api/v1/movies/search/?q=том+хенкс&page=1
    Єдиний пошук — повертає фільми, серіали і персони.
    Кожен елемент має поле media_type: "movie" | "tv" | "person"
    """
    q = request.query_params.get('q', '').strip()
    page = int(request.query_params.get('page', 1))
    if not q:
        return Response({'error': "Параметр 'q' обов'язковий"}, status=400)
    data = tmdb.multi_search(q, page=page)
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
            user=request.user, tmdb_id=movie_id, media_type=media_type).exists()
        user_state['is_favorite'] = FavoriteMovie.objects.filter(
            user=request.user, tmdb_id=movie_id, media_type=media_type).exists()
        rating = MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id, media_type=media_type).first()
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

    qp = request.query_params

    allowed_simple = [
        'with_genres', 'primary_release_year', 'first_air_date_year',
        'sort_by', 'page', 'with_original_language', 'vote_count_gte',
    ]
    filters = {k: qp[k] for k in allowed_simple if k in qp}

    dot_params = {
        'vote_average_gte':         'vote_average.gte',
        'vote_average_lte':         'vote_average.lte',
        'primary_release_date_gte': 'primary_release_date.gte',
        'primary_release_date_lte': 'primary_release_date.lte',
        'first_air_date_gte':       'first_air_date.gte',
        'first_air_date_lte':       'first_air_date.lte',
    }
    for frontend_key, tmdb_key in dot_params.items():
        if frontend_key in qp:
            filters[tmdb_key] = qp[frontend_key]

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


# ═══════════════════════════════════════════════════════════════════════════════
# ПЕРСОНИ (актори, режисери, etc.)
# ═══════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def person_detail(request, person_id):
    """
    GET /api/v1/movies/persons/<person_id>/
    Повна інформація про персону: біографія, фото, movie_credits, tv_credits
    """
    data = tmdb.get_person(person_id)
    if data is None:
        return Response({'error': 'Персону не знайдено'}, status=404)
    return Response(data)


# ═══════════════════════════════════════════════════════════════════════════════
# WATCHLIST / FAVORITES / RATINGS
# ═══════════════════════════════════════════════════════════════════════════════

@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_watchlist(request, movie_id):
    media_type = request.data.get(
        'media_type', request.query_params.get('media_type', 'movie'))

    item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        tmdb_id=movie_id,
        media_type=media_type,
        defaults=_fetch_item_data(movie_id, media_type)
    )
    if not created:
        item.delete()
        return Response({'in_watchlist': False})
    return Response({'in_watchlist': True}, status=201)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, movie_id):
    media_type = request.data.get(
        'media_type', request.query_params.get('media_type', 'movie'))

    item, created = FavoriteMovie.objects.get_or_create(
        user=request.user,
        tmdb_id=movie_id,
        media_type=media_type,
        defaults=_fetch_item_data(movie_id, media_type)
    )
    if not created:
        item.delete()
        return Response({'is_favorite': False})
    return Response({'is_favorite': True}, status=201)


@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def movie_rating(request, movie_id):
    media_type = request.data.get(
        'media_type', request.query_params.get('media_type', 'movie'))

    if request.method == 'DELETE':
        MovieRating.objects.filter(
            user=request.user, tmdb_id=movie_id, media_type=media_type
        ).delete()
        return Response({'user_rating': None})

    rating = request.data.get('rating')
    if rating is None:
        return Response({'error': "Поле 'rating' обов'язкове"}, status=400)
    try:
        rating = int(rating)
        if not 1 <= rating <= 10:
            raise ValueError
    except (ValueError, TypeError):
        return Response({'error': 'Рейтинг має бути числом від 1 до 10'}, status=400)

    item_data = _fetch_item_data(movie_id, media_type)

    obj, created = MovieRating.objects.update_or_create(
        user=request.user,
        tmdb_id=movie_id,
        media_type=media_type,
        defaults={
            'rating': rating,
            'review': request.data.get('review', ''),
            'title': item_data['title'],
            'poster_path': item_data['poster_path'],
        }
    )
    return Response({'user_rating': obj.rating}, status=201 if created else 200)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_watchlist(request, username):
    """GET /api/v1/movies/users/<username>/watchlist/"""
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    items = WatchlistItem.objects.filter(user=user).order_by('-added_at')
    data = [
        {
            'tmdb_id':    i.tmdb_id,
            'title':      i.title,
            'poster_path': i.poster_path,
            'poster_url': f'https://image.tmdb.org/t/p/w342{i.poster_path}' if i.poster_path else None,
            'media_type': i.media_type,
            'added_at':   i.added_at,
        }
        for i in items
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_favorites(request, username):
    """GET /api/v1/movies/users/<username>/favorites/"""
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    items = FavoriteMovie.objects.filter(user=user).order_by('-added_at')
    data = [
        {
            'tmdb_id':    i.tmdb_id,
            'title':      i.title,
            'poster_path': i.poster_path,
            'poster_url': f'https://image.tmdb.org/t/p/w342{i.poster_path}' if i.poster_path else None,
            'media_type': i.media_type,
            'added_at':   i.added_at,
        }
        for i in items
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_ratings(request, username):
    """GET /api/v1/movies/users/<username>/ratings/"""
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    items = MovieRating.objects.filter(user=user).order_by('-added_at')
    data = [
        {
            'tmdb_id':    i.tmdb_id,
            'title':      i.title,
            'poster_path': i.poster_path,
            'poster_url': f'https://image.tmdb.org/t/p/w342{i.poster_path}' if i.poster_path else None,
            'media_type': i.media_type,
            'rating':     i.rating,
            'added_at':   i.added_at,
        }
        for i in items
    ]
    return Response(data)


# ─── Списки юзера ─────────────────────────────────────────────────────────────

class MyWatchlistView(generics.ListAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = WatchlistItem.objects.filter(user=self.request.user)
        media_type = self.request.query_params.get('media_type')
        if media_type in ('movie', 'tv'):
            qs = qs.filter(media_type=media_type)
        return qs


class MyFavoritesView(generics.ListAPIView):
    serializer_class = FavoriteMovieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FavoriteMovie.objects.filter(user=self.request.user)
        media_type = self.request.query_params.get('media_type')
        if media_type in ('movie', 'tv'):
            qs = qs.filter(media_type=media_type)
        return qs


class MyRatingsView(generics.ListAPIView):
    serializer_class = MovieRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = MovieRating.objects.filter(user=self.request.user)
        media_type = self.request.query_params.get('media_type')
        if media_type in ('movie', 'tv'):
            qs = qs.filter(media_type=media_type)
        return qs
