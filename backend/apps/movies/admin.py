from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import WatchlistItem, FavoriteMovie, MovieRating


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = (
        'user_link',
        'title_with_poster',
        'media_type',
        'tmdb_id',
        'added_at',
    )
    list_display_links = ('title_with_poster',)
    list_filter = (
        'media_type',
        'added_at',
        'user',
    )
    search_fields = (
        'user__username',
        'user__email',
        'title',
        'tmdb_id',
    )
    readonly_fields = ('added_at', 'tmdb_id', 'media_type')
    list_per_page = 30
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    user_link.short_description = "Користувач"

    def title_with_poster(self, obj):
        if obj.poster_url:
            return format_html(
                '<img src="{}" style="height:48px; border-radius:4px; margin-right:8px; vertical-align:middle;"> {}',
                obj.poster_url, obj.title
            )
        return obj.title
    title_with_poster.short_description = "Назва"

    actions = ['delete_selected_with_message']

    def delete_selected_with_message(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request, f"Видалено {count} елементів зі списку 'Хочу дивитись'.")
    delete_selected_with_message.short_description = "Видалити вибрані (з повідомленням)"


@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = (
        'user_link',
        'title_with_poster',
        'media_type',
        'tmdb_id',
        'added_at',
    )
    list_display_links = ('title_with_poster',)
    list_filter = (
        'media_type',
        'added_at',
        'user',
    )
    search_fields = (
        'user__username',
        'user__email',
        'title',
        'tmdb_id',
    )
    readonly_fields = ('added_at', 'tmdb_id', 'media_type')
    list_per_page = 30
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    user_link.short_description = "Користувач"

    def title_with_poster(self, obj):
        if obj.poster_url:
            return format_html(
                '<img src="{}" style="height:48px; border-radius:4px; margin-right:8px; vertical-align:middle;"> {}',
                obj.poster_url, obj.title
            )
        return obj.title
    title_with_poster.short_description = "Назва"

    actions = ['delete_selected_with_message']

    def delete_selected_with_message(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Видалено {count} улюблених елементів.")
    delete_selected_with_message.short_description = "Видалити вибрані улюблені"


@admin.register(MovieRating)
class MovieRatingAdmin(admin.ModelAdmin):
    list_display = (
        'user_link',
        'title_with_poster',
        'rating_stars',
        'media_type',
        'added_at',
        'updated_at',
    )
    list_display_links = ('title_with_poster',)
    list_filter = (
        'media_type',
        'rating',
        'added_at',
        'user',
    )
    search_fields = (
        'user__username',
        'user__email',
        'title',
        'tmdb_id',
        'review',
    )
    readonly_fields = ('added_at', 'updated_at', 'tmdb_id', 'media_type')
    list_per_page = 25
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'tmdb_id', 'media_type', 'rating', 'review')
        }),
        ('Технічна інформація', {
            'classes': ('collapse',),
            'fields': ('poster_path', 'added_at', 'updated_at'),
        }),
    )

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id, obj.user.username
        )
    user_link.short_description = "Користувач"

    def title_with_poster(self, obj):
        if obj.poster_url:
            return format_html(
                '<img src="{}" style="height:48px; border-radius:4px; margin-right:8px; vertical-align:middle;"> {}',
                obj.poster_url, obj.title or "—"
            )
        return obj.title or "—"
    title_with_poster.short_description = "Назва"

    def rating_stars(self, obj):
        return format_html('★' * obj.rating + '☆' * (10 - obj.rating))
    rating_stars.short_description = "Оцінка"

    actions = ['set_rating_to_10', 'delete_selected_with_message']

    def set_rating_to_10(self, request, queryset):
        updated = queryset.update(rating=10)
        self.message_user(request, f"Оновлено {updated} оцінок до 10/10.")
    set_rating_to_10.short_description = "Поставити оцінку 10/10 вибраним"

    def delete_selected_with_message(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Видалено {count} оцінок.")
    delete_selected_with_message.short_description = "Видалити вибрані оцінки"
