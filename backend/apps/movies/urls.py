# apps/movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.movie_search, name='movie-search'),
    path('trending/', views.movie_trending, name='movie-trending'),
    path('genres/', views.movie_genres, name='movie-genres'),
    path('discover/', views.movie_discover, name='movie-discover'),

    path('me/watchlist/', views.MyWatchlistView.as_view(), name='my-watchlist'),
    path('me/favorites/', views.MyFavoritesView.as_view(), name='my-favorites'),

    path('<int:movie_id>/', views.movie_detail, name='movie-detail'),
    path('<int:movie_id>/watchlist/',
         views.toggle_watchlist, name='toggle-watchlist'),
    path('<int:movie_id>/favorite/', views.toggle_favorite, name='toggle-favorite'),
    path('<int:movie_id>/rate/', views.movie_rating, name='movie-rating'),

    path('<str:category>/', views.movie_list_by_category, name='movie-category'),
]
