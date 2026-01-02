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
app_name = 'posts'

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


# ============================================
# ЧОМУ САМЕ ТАК? (ПОЯСНЕННЯ)
# ============================================

"""
1. DefaultRouter vs SimpleRouter:
   
   DefaultRouter створює:
   - /api/                  (API root - список всіх ендпоінтів)
   - /api/categories/       (ресурси)
   - /api/categories.json   (різні формати)
   
   SimpleRouter створює:
   - /api/categories/       (тільки ресурси)
   
   ✅ Використовуй DefaultRouter - зручніше для розробки


2. basename - навіщо?
   
   basename використовується для:
   - Генерації назв URL (для reverse())
   - Унікальної ідентифікації роутів
   
   Приклад:
   router.register(r'posts', PostViewSet, basename='post')
   
   Створює назви:
   - post-list       (GET /posts/)
   - post-detail     (GET /posts/{slug}/)
   - post-my         (GET /posts/my/)
   
   У коді можна використати:
   from django.urls import reverse
   url = reverse('posts:post-list')  # /api/posts/


3. NestedDefaultRouter - для чого?
   
   Створює ієрархічні URL:
   /posts/{post_slug}/images/
   
   Без нього треба було б:
   /images/?post_slug=my-post  ❌ Не REST-like
   
   З ним:
   /posts/my-post/images/      ✅ Красиво і зрозуміло


4. lookup='post' - що це?
   
   Це назва параметру в URL:
   lookup='post' → {post_slug}
   
   В ViewSet отримуєш:
   self.kwargs['post_slug']
   
   Можна змінити:
   lookup='article' → {article_slug}
   self.kwargs['article_slug']
"""


# ============================================
# ЯК ПЕРЕВІРИТИ ЩО СТВОРИЛОСЬ?
# ============================================

"""
Після того як створив urls.py, запусти в терміналі:

python manage.py show_urls

Або встанови django-extensions:
pip install django-extensions

І запусти:
python manage.py show_urls | grep posts

Побачиш всі URL що створились!

Приклад виводу:
/api/posts/                          posts:post-list
/api/posts/<slug>/                   posts:post-detail
/api/posts/my/                       posts:post-my
/api/posts/<slug>/images/            posts:post-images-list
/api/posts/<slug>/images/<pk>/       posts:post-images-detail
"""


# ============================================
# АЛЬТЕРНАТИВНИЙ ВАРІАНТ (БЕЗ NESTED ROUTER)
# ============================================

"""
Якщо не хочеш встановлювати drf-nested-routers,
можна зробити так:

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'posts', views.PostViewSet, basename='post')

app_name = 'posts'

urlpatterns = [
    path('', include(router.urls)),
    
    # Зображення - вручну
    path('posts/<slug:post_slug>/images/',
         views.PostImagesViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='post-images-list'),
    path('posts/<slug:post_slug>/images/<int:pk>/',
         views.PostImagesViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='post-images-detail'),
    path('posts/<slug:post_slug>/images/reorder/',
         views.PostImagesViewSet.as_view({'patch': 'reorder'}),
         name='post-images-reorder'),
    
    # Відео - вручну
    path('posts/<slug:post_slug>/videos/',
         views.PostVideosViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='post-videos-list'),
    path('posts/<slug:post_slug>/videos/<int:pk>/',
         views.PostVideosViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
         name='post-videos-detail'),
    
    # Додаткові
    path('posts/popular/', views.popular_posts, name='popular-posts'),
    path('posts/trending/', views.trending_posts, name='trending-posts'),
]

❌ НЕДОЛІКИ:
- Багато повторів
- Легко зробити помилку
- Важко підтримувати

✅ З NESTED ROUTER:
- 2 рядки коду
- Все автоматично
- Легко розширювати

ВИСНОВОК: Краще встановити drf-nested-routers!
pip install drf-nested-routers
"""


# ============================================
# ФІНАЛЬНА РЕКОМЕНДАЦІЯ ⭐
# ============================================

"""
ВИКОРИСТОВУЙ:

1. Router для ViewSets (categories, posts)
   → Автоматично створює всі CRUD URLs
   
2. NestedRouter для вкладених ресурсів (images, videos)
   → Створює гарні ієрархічні URLs
   
3. Path для простих функцій (popular, trending)
   → Коли не потрібен повний CRUD

Це найкращий баланс між:
- Автоматизацією (менше коду)
- Гнучкістю (можна додавати власні URLs)
- Читабельністю (зрозуміла структура)
"""
