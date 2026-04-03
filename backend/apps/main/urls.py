from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# ============================================
# КРОК 1: Створюємо головний роутер
# ============================================
router = DefaultRouter()

# ============================================
# КРОК 2: Реєструємо ViewSets
# ============================================
# Синтаксис: router.register(r'url-prefix', ViewSetClass, basename='назва')

router.register(
    r'categories',              # URL буде: /api/categories/
    views.CategoryViewSet,      # Який ViewSet використовувати
    basename='category'         # Базова назва для reverse()
)

router.register(
    r'posts',                   # URL буде: /api/posts/
    views.PostViewSet,
    basename='post'
)

# ============================================
# КРОК 3: Створюємо вкладений роутер для медіа
# ============================================
# Це створює URLs типу: /posts/{slug}/images/

posts_router = routers.NestedDefaultRouter(
    router,         # Батьківський роутер (той, що створили вище)
    r'posts',       # Батьківський resource (posts)
    lookup='post'   # Назва параметру: post_slug (буде post + _slug)
)

# Реєструємо зображення
posts_router.register(
    r'images',                  # URL: /api/posts/{post_slug}/images/
    views.PostImagesViewSet,
    basename='post-images'
)

# Реєструємо відео
posts_router.register(
    r'videos',                  # URL: /api/posts/{post_slug}/videos/
    views.PostVideosViewSet,
    basename='post-videos'
)

# ============================================
# КРОК 4: Збираємо всі URLs разом
# ============================================

urlpatterns = [
    path('posts/popular/', views.popular_posts, name='popular-posts'),
    path('posts/trending/', views.trending_posts, name='trending-posts'),

    # Router URLs (автоматично генеруються)
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
]


# ============================================
# ПОВНИЙ СПИСОК URL, ЩО СТВОРЮЮТЬСЯ
# ============================================

"""
АВТОМАТИЧНО СТВОРЕНІ (через router):
=====================================

КАТЕГОРІЇ:
----------
GET     /api/categories/                    # CategoryViewSet.list()
POST    /api/categories/                    # CategoryViewSet.create()
GET     /api/categories/{slug}/             # CategoryViewSet.retrieve()
PUT     /api/categories/{slug}/             # CategoryViewSet.update()
PATCH   /api/categories/{slug}/             # CategoryViewSet.partial_update()
DELETE  /api/categories/{slug}/             # CategoryViewSet.destroy()

ПОСТИ:
------
GET     /api/posts/                         # PostViewSet.list()
POST    /api/posts/                         # PostViewSet.create()
GET     /api/posts/{slug}/                  # PostViewSet.retrieve()
PUT     /api/posts/{slug}/                  # PostViewSet.update()
PATCH   /api/posts/{slug}/                  # PostViewSet.partial_update()
DELETE  /api/posts/{slug}/                  # PostViewSet.destroy()

# Додаткові actions (через @action декоратор):
GET     /api/posts/my/                      # PostViewSet.my()
GET     /api/posts/by_tag/?tag=python       # PostViewSet.by_tag()

ЗОБРАЖЕННЯ (вкладені):
----------------------
GET     /api/posts/{post_slug}/images/          # PostImagesViewSet.list()
POST    /api/posts/{post_slug}/images/          # PostImagesViewSet.create()
GET     /api/posts/{post_slug}/images/{id}/     # PostImagesViewSet.retrieve()
PUT     /api/posts/{post_slug}/images/{id}/     # PostImagesViewSet.update()
PATCH   /api/posts/{post_slug}/images/{id}/     # PostImagesViewSet.partial_update()
DELETE  /api/posts/{post_slug}/images/{id}/     # PostImagesViewSet.destroy()

# Actions:
PATCH   /api/posts/{post_slug}/images/reorder/      # PostImagesViewSet.reorder()
DELETE  /api/posts/{post_slug}/images/bulk_delete/  # PostImagesViewSet.bulk_delete()

ВІДЕО (вкладені):
-----------------
GET     /api/posts/{post_slug}/videos/          # PostVideosViewSet.list()
POST    /api/posts/{post_slug}/videos/          # PostVideosViewSet.create()
GET     /api/posts/{post_slug}/videos/{id}/     # PostVideosViewSet.retrieve()
DELETE  /api/posts/{post_slug}/videos/{id}/     # PostVideosViewSet.destroy()

# Actions:
PATCH   /api/posts/{post_slug}/videos/reorder/      # PostVideosViewSet.reorder()
DELETE  /api/posts/{post_slug}/videos/bulk_delete/  # PostVideosViewSet.bulk_delete()

СТВОРЕНІ ВРУЧНУ (через path):
==============================
GET     /api/posts/popular/                 # popular_posts()
GET     /api/posts/trending/                # trending_posts()
"""
