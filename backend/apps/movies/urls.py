from django.urls import path
from . import views

urlpatterns = [
    # --- Конкретні маршрути ПЕРШИМИ ---
    path('search/',       views.movie_search,   name='movie-search'),
    path('trending/',     views.movie_trending, name='movie-trending'),
    path('genres/',       views.movie_genres,   name='movie-genres'),
    path('discover/',     views.movie_discover, name='movie-discover'),

    # --- me/ маршрути ---
    path('me/watchlist/', views.MyWatchlistView.as_view(), name='my-watchlist'),
    path('me/favorites/', views.MyFavoritesView.as_view(), name='my-favorites'),

    # --- Категорії (рядкові, але конкретні) ---
    path('popular/',     views.movie_list_by_category,
         {'category': 'popular'},     name='movie-popular'),
    path('top_rated/',   views.movie_list_by_category,
         {'category': 'top_rated'},   name='movie-top-rated'),
    path('upcoming/',    views.movie_list_by_category,
         {'category': 'upcoming'},     name='movie-upcoming'),
    path('now_playing/', views.movie_list_by_category,
         {'category': 'now_playing'},  name='movie-now-playing'),
    path('on_the_air/',  views.movie_list_by_category,
         {'category': 'on_the_air'},   name='movie-on-the-air'),

    # --- Числові ID ---
    path('<int:movie_id>/',
         views.movie_detail,          name='movie-detail'),
    path('<int:movie_id>/watchlist/',
         views.toggle_watchlist,      name='toggle-watchlist'),
    path('<int:movie_id>/favorite/',
         views.toggle_favorite,       name='toggle-favorite'),
    path('<int:movie_id>/rate/',
         views.movie_rating,          name='movie-rating'),
    path('<int:movie_id>/recommendations/',
         views.movie_recommendations,  name='movie-recommendations'),
]
