import httpx
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"


class TMDBClient:
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', '')
        self.base_url = TMDB_BASE_URL
        self.language = "uk-UA"

    def _get(self, endpoint: str, params: dict = None) -> dict | None:
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        params.setdefault("language", self.language)
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"TMDB HTTP {e.response.status_code}: {endpoint}")
            return None
        except httpx.RequestError as e:
            logger.error(f"TMDB request error: {e}")
            return None

    def _cached_get(self, cache_key, endpoint, params=None, timeout=3600):
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        data = self._get(endpoint, params)
        if data:
            cache.set(cache_key, data, timeout)
        return data

    # Пошук (movie або tv)
    def search(self, query: str, page: int = 1, media_type: str = 'movie') -> dict | None:
        cache_key = f"tmdb:search:{media_type}:{query}:{page}"
        return self._cached_get(cache_key, f"/search/{media_type}", {"query": query, "page": page}, 1800)

    # Деталі фільму
    def get_movie(self, movie_id: int) -> dict | None:
        cache_key = f"tmdb:movie:{movie_id}"
        return self._cached_get(
            cache_key,
            f"/movie/{movie_id}",
            {
                # language НЕ передаємо через setdefault — override нижче
                "language": "uk-UA",
                "append_to_response": "videos,credits,similar,recommendations,images",
                # Відео: англійські + без мови (найбільше трейлерів)
                "include_video_language": "uk,en",
                # Зображення: українські + англійські + без мовного маркування
                "include_image_language": "uk,en,null",
            },
            86400
        )

    # Деталі серіалу
    def get_tv(self, tv_id: int) -> dict | None:
        cache_key = f"tmdb:tv:{tv_id}"
        return self._cached_get(
            cache_key,
            f"/tv/{tv_id}",
            {
                "language": "uk-UA",
                "append_to_response": "videos,credits,similar,recommendations,images",
                "include_video_language": "uk,en",
                "include_image_language": "uk,en,null",
            },
            86400
        )

    # Trending
    def get_trending(self, media_type='movie', time_window='week') -> dict | None:
        cache_key = f"tmdb:trending:{media_type}:{time_window}"
        return self._cached_get(cache_key, f"/trending/{media_type}/{time_window}", timeout=3600)

    # Списки
    def get_popular(self, page=1, media_type='movie') -> dict | None:
        cache_key = f"tmdb:popular:{media_type}:{page}"
        return self._cached_get(cache_key, f"/{media_type}/popular", {"page": page}, 3600)

    def get_top_rated(self, page=1, media_type='movie') -> dict | None:
        cache_key = f"tmdb:top_rated:{media_type}:{page}"
        return self._cached_get(cache_key, f"/{media_type}/top_rated", {"page": page}, 3600)

    def get_upcoming(self, page=1) -> dict | None:
        cache_key = f"tmdb:upcoming:{page}"
        return self._cached_get(cache_key, "/movie/upcoming", {"page": page}, 3600)

    def get_now_playing(self, page=1) -> dict | None:
        cache_key = f"tmdb:now_playing:{page}"
        return self._cached_get(cache_key, "/movie/now_playing", {"page": page}, 3600)

    def get_on_the_air(self, page=1) -> dict | None:
        cache_key = f"tmdb:on_the_air:{page}"
        return self._cached_get(cache_key, "/tv/on_the_air", {"page": page}, 3600)

    # Жанри
    def get_genres(self, media_type='movie') -> dict | None:
        cache_key = f"tmdb:genres:{media_type}"
        return self._cached_get(cache_key, f"/genre/{media_type}/list", timeout=86400)

    # Discover
    def discover(self, media_type='movie', **filters) -> dict | None:
        cache_key = f"tmdb:discover:{media_type}:{hash(frozenset(filters.items()))}"
        return self._cached_get(cache_key, f"/discover/{media_type}", filters, 1800)

    # Рекомендації
    def get_recommendations(self, item_id: int, media_type='movie') -> dict | None:
        cache_key = f"tmdb:recommendations:{media_type}:{item_id}"
        return self._cached_get(cache_key, f"/{media_type}/{item_id}/recommendations", timeout=3600)

    @staticmethod
    def image_url(path: str, size: str = "w500") -> str | None:
        if not path:
            return None
        return f"{TMDB_IMAGE_BASE}/{size}{path}"


tmdb = TMDBClient()
