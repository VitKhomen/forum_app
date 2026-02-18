# apps/movies/services/tmdb_client.py
import httpx
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


class TMDBClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.language = "uk-UA"  # або "en-US"

    def _get(self, endpoint: str, params: dict = None) -> dict | None:
        """Базовий метод GET запиту"""
        if params is None:
            params = {}

        params["api_key"] = self.api_key
        params["language"] = self.language

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"TMDB HTTP error {e.response.status_code}: {endpoint}")
            return None
        except httpx.RequestError as e:
            logger.error(f"TMDB request error: {e}")
            return None

    def _cached_get(self, cache_key: str, endpoint: str, params: dict = None, timeout: int = 3600):
        """GET з кешуванням через Django cache framework"""
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._get(endpoint, params)
        if data:
            cache.set(cache_key, data, timeout)
        return data

    # ─── Пошук ──────────────────────────────────────────────────
    def search_movies(self, query: str, page: int = 1) -> dict | None:
        cache_key = f"tmdb:search:{query}:{page}"
        return self._cached_get(
            cache_key,
            "/search/movie",
            {"query": query, "page": page},
            timeout=1800  # 30 хвилин
        )

    # ─── Деталі фільму ───────────────────────────────────────────
    def get_movie(self, movie_id: int) -> dict | None:
        cache_key = f"tmdb:movie:{movie_id}"
        return self._cached_get(
            cache_key,
            f"/movie/{movie_id}",
            {"append_to_response": "videos,images,credits,similar"},
            timeout=86400  # 24 години
        )

    # ─── Списки ─────────────────────────────────────────────────
    def get_trending(self, time_window: str = "week") -> dict | None:
        cache_key = f"tmdb:trending:{time_window}"
        return self._cached_get(
            cache_key,
            f"/trending/movie/{time_window}",
            timeout=3600
        )

    def get_popular(self, page: int = 1) -> dict | None:
        cache_key = f"tmdb:popular:{page}"
        return self._cached_get(cache_key, "/movie/popular", {"page": page}, timeout=3600)

    def get_top_rated(self, page: int = 1) -> dict | None:
        cache_key = f"tmdb:top_rated:{page}"
        return self._cached_get(cache_key, "/movie/top_rated", {"page": page}, timeout=3600)

    def get_upcoming(self, page: int = 1) -> dict | None:
        cache_key = f"tmdb:upcoming:{page}"
        return self._cached_get(cache_key, "/movie/upcoming", {"page": page}, timeout=3600)

    def get_now_playing(self, page: int = 1) -> dict | None:
        cache_key = f"tmdb:now_playing:{page}"
        return self._cached_get(cache_key, "/movie/now_playing", {"page": page}, timeout=3600)

    # ─── Жанри ──────────────────────────────────────────────────
    def get_genres(self) -> dict | None:
        cache_key = "tmdb:genres"
        return self._cached_get(cache_key, "/genre/movie/list", timeout=86400)

    # ─── Фільтрація ─────────────────────────────────────────────
    def discover_movies(self, **filters) -> dict | None:
        """
        filters: genre_ids, year, sort_by, page, etc.
        Приклад: discover_movies(with_genres="28,12", primary_release_year=2024)
        """
        cache_key = f"tmdb:discover:{hash(frozenset(filters.items()))}"
        return self._cached_get(
            cache_key,
            "/discover/movie",
            filters,
            timeout=1800
        )

    # ─── Хелпери для зображень ──────────────────────────────────
    @staticmethod
    def image_url(path: str, size: str = "w500") -> str | None:
        """
        Розміри постерів: w92, w154, w185, w342, w500, w780, original
        Розміри бекдропів: w300, w780, w1280, original
        """
        if not path:
            return None
        return f"{TMDB_IMAGE_BASE}/{size}{path}"


# Синглтон — один екземпляр на весь проект
tmdb = TMDBClient()
