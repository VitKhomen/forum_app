from django.contrib import admin
from django.utils.html import format_html
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read_badge')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    date_hierarchy = 'created_at'  # ✅ Фільтр по даті
    list_per_page = 50

    fieldsets = (
        ('Інформація про відправника', {
            'fields': ('name', 'email')
        }),
        ('Повідомлення', {
            'fields': ('subject', 'message')
        }),
        ('Статус', {
            'fields': ('is_read', 'created_at')
        }),
    )

    def is_read_badge(self, obj):
        """Кольоровий badge для статусу"""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Прочитано</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Не прочитано</span>'
        )
    is_read_badge.short_description = 'Статус'
    is_read_badge.admin_order_field = 'is_read'

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='✓ Позначити як прочитані')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request, f'✓ Позначено {updated} повідомлень як прочитані')

    @admin.action(description='✗ Позначити як непрочитані')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(
            request, f'✗ Позначено {updated} повідомлень як непрочитані')

    def has_add_permission(self, request):
        return False  # ✅ Не можна створювати через адмінку
