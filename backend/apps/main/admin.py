from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse

from .models import Category, Post, PostImages, PostVideo

User = get_user_model()


# ============================================
# USER ADMIN (потрібен для autocomplete)
# ============================================

# Перевіряємо чи User вже зареєстрований
if not admin.site.is_registered(User):
    @admin.register(User)
    class UserAdmin(admin.ModelAdmin):
        """Базовий адмін для User (потрібен для autocomplete)"""
        list_display = ('username', 'email', 'first_name',
                        'last_name', 'is_staff')
        search_fields = ('username', 'email', 'first_name',
                         'last_name')  # ← Для autocomplete
        list_filter = ('is_staff', 'is_active', 'date_joined')


# ============================================
# INLINE АДМІНІСТРУВАННЯ (вкладені таблиці)
# ============================================

class PostImagesInline(admin.TabularInline):
    """
    Дозволяє редагувати зображення прямо на сторінці поста
    """
    model = PostImages
    extra = 1  # Скільки порожніх форм показувати
    fields = ('image', 'order', 'image_preview')
    readonly_fields = ('image_preview', 'created_at')
    ordering = ('order',)

    def image_preview(self, obj):
        """Показує мініатюру зображення"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;"/>',
                obj.image.url
            )
        return "Немає зображення"
    image_preview.short_description = "Прев'ю"


class PostVideoInline(admin.TabularInline):
    """Вкладена таблиця для відео"""
    model = PostVideo
    extra = 1
    fields = ('video', 'order', 'video_link')
    readonly_fields = ('video_link', 'created_at')
    ordering = ('order',)

    def video_link(self, obj):
        """Показує посилання на відео"""
        if obj.video:
            return format_html(
                '<a href="{}" target="_blank">Переглянути відео</a>',
                obj.video.url
            )
        return "Немає відео"
    video_link.short_description = "Посилання"


# ============================================
# CATEGORY ADMIN
# ============================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Адмін панель для категорій"""

    list_display = ('name', 'slug', 'posts_count', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'description')  # ← Для autocomplete
    list_filter = ('created_at',)
    readonly_fields = ('slug', 'created_at', 'posts_count')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Статистика', {
            'fields': ('posts_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def posts_count(self, obj):
        """Кількість постів у категорії"""
        count = obj.posts.count()
        if count > 0:
            url = reverse('admin:main_post_changelist') + \
                f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} постів</a>', url, count)
        return '0 постів'
    posts_count.short_description = 'Кількість постів'


# ============================================
# POST ADMIN
# ============================================

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Адмін панель для постів"""

    # Список полів в таблиці
    list_display = (
        'title',
        'author',
        'category',
        'status_badge',  # ← Використовуємо badge замість status
        'views_count',
        'images_count',
        'videos_count',
        'published_at',
        'created_at'
    )

    list_display_links = ('title',)

    # Поля для пошуку
    search_fields = ('title', 'content', 'author__username', 'tags__name')

    # Фільтри
    list_filter = (
        'status',
        'category',
        'created_at',
        'published_at',
        'tags'
    )

    # Поля тільки для читання
    readonly_fields = (
        'slug',
        'created_at',
        'updated_at',
        'published_at',
        'views_count',
        'image_preview',
        'post_link'
    )

    # Автозаповнення
    prepopulated_fields = {'slug': ('title',)}

    # ❌ Видалили list_editable (бо status_badge не можна редагувати)
    # Замість цього використовуємо actions для зміни статусу

    # Дії які можна виконати над вибраними постами
    actions = ['make_published', 'make_draft', 'reset_views']

    # Скільки постів на сторінку
    list_per_page = 25

    # Сортування за замовчуванням
    ordering = ('-created_at',)

    # ✅ Autocomplete (тепер працює, бо User і Category мають search_fields)
    autocomplete_fields = ['author', 'category']

    # Фільтр по датах
    date_hierarchy = 'created_at'

    # Вкладені таблиці
    inlines = [PostImagesInline, PostVideoInline]

    # Групування полів
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Контент', {
            'fields': ('content', 'image', 'image_preview', 'tags')
        }),
        ('Метадані', {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Посилання', {
            'fields': ('post_link',),
            'classes': ('collapse',)
        }),
    )

    # Кастомні методи для відображення

    def status_badge(self, obj):
        """Кольоровий badge статусу"""
        if obj.status == 'published':
            color = '#28a745'  # зелений
            text = '✅ Опубліковано'
        else:
            color = '#6c757d'  # сірий
            text = '📝 Чернетка'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; display: inline-block;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'  # Дозволяє сортувати по цьому полю

    def image_preview(self, obj):
        """Прев'ю головного зображення"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;"/>',
                obj.image.url
            )
        return "Немає зображення"
    image_preview.short_description = "Прев'ю зображення"

    def images_count(self, obj):
        """Кількість додаткових зображень"""
        count = obj.images.count()
        if count > 0:
            return format_html('<b style="color: #007bff;">{}</b> 📷', count)
        return '0'
    images_count.short_description = 'Зображень'

    def videos_count(self, obj):
        """Кількість відео"""
        count = obj.videos.count()
        if count > 0:
            return format_html('<b style="color: #dc3545;">{}</b> 🎥', count)
        return '0'
    videos_count.short_description = 'Відео'

    def post_link(self, obj):
        """Посилання на пост на сайті"""
        if obj.slug:
            try:
                url = obj.get_absolute_url()
                return format_html(
                    '<a href="{}" target="_blank" style="color: #007bff;">🔗 Переглянути на сайті →</a>',
                    url
                )
            except:
                return "Налаштуйте get_absolute_url()"
        return "Збережіть пост щоб отримати посилання"
    post_link.short_description = 'Посилання на сайт'

    # Кастомні actions (дії)

    @admin.action(description='✅ Опублікувати вибрані пости')
    def make_published(self, request, queryset):
        """Масова публікація постів"""
        from django.utils import timezone

        updated = 0
        for post in queryset:
            if post.status != 'published':
                post.status = 'published'
                if not post.published_at:
                    post.published_at = timezone.now()
                post.save()
                updated += 1

        self.message_user(
            request,
            f'✅ Опубліковано {updated} постів',
            level='success'
        )

    @admin.action(description='📝 Зробити чернетками')
    def make_draft(self, request, queryset):
        """Масове перетворення в чернетки"""
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(
            request,
            f'📝 Змінено статус у {updated} постів на "Чернетка"',
            level='success'
        )

    @admin.action(description='🔄 Скинути перегляди')
    def reset_views(self, request, queryset):
        """Скидання лічильника переглядів"""
        updated = queryset.update(views_count=0)
        self.message_user(
            request,
            f'🔄 Скинуто перегляди у {updated} постів',
            level='warning'
        )

    def get_queryset(self, request):
        """Оптимізація запитів"""
        qs = super().get_queryset(request)
        return qs.select_related('author', 'category') \
                 .prefetch_related('tags', 'images', 'videos')


# ============================================
# POST IMAGES ADMIN (окремо)
# ============================================

@admin.register(PostImages)
class PostImagesAdmin(admin.ModelAdmin):
    """Окреме адміністрування зображень"""

    list_display = ('post_title', 'image_preview', 'order', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('post__title',)
    readonly_fields = ('created_at', 'image_preview')
    list_per_page = 50
    autocomplete_fields = ['post']

    def post_title(self, obj):
        """Заголовок поста"""
        return obj.post.title
    post_title.short_description = 'Пост'
    post_title.admin_order_field = 'post__title'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;"/>',
                obj.image.url
            )
        return "Немає зображення"
    image_preview.short_description = "Прев'ю"


# ============================================
# POST VIDEO ADMIN (окремо)
# ============================================

@admin.register(PostVideo)
class PostVideoAdmin(admin.ModelAdmin):
    """Окреме адміністрування відео"""

    list_display = ('post_title', 'video_name', 'order', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('post__title',)
    readonly_fields = ('created_at',)
    list_per_page = 50
    autocomplete_fields = ['post']

    def post_title(self, obj):
        """Заголовок поста"""
        return obj.post.title
    post_title.short_description = 'Пост'
    post_title.admin_order_field = 'post__title'

    def video_name(self, obj):
        if obj.video:
            return obj.video.name.split('/')[-1]
        return "Немає відео"
    video_name.short_description = "Файл"
