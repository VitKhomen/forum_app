import httpx
import redis
import json
from django.conf import settings

r = redis.Redis(host='localhost', port=6379)


def get_movies_tmdb(query):
    key = f"tmdb:{query}"

    # 1) попробуем взять из кеша
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    # 2) если нет — запросим API
    with httpx.Client() as client:
        res = client.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": settings.TMDB_API_KEY,
                "query": query
            }
        )

    data = res.json()

    # 3) сохраним в кеш на 1 час
    r.set(key, json.dumps(data), ex=3600)

    return data
