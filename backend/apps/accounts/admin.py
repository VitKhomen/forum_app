from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'full_name_display',
        'avatar_preview',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_superuser',
                   'is_active', 'groups', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'created_at',
                       'updated_at', 'avatar_preview')

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Особиста інформація', {
            'fields': ('first_name', 'last_name', 'avatar', 'avatar_preview', 'bio')
        }),
        ('Права доступу', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важливі дати', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # згорнутий блок
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

    # Попередній перегляд аватара в списку та формі
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="border-radius: 50%; object-fit: cover; width: 40px; height: 40px;" />',
                obj.avatar.url
            )
        return "(Немає аватара)"
    avatar_preview.short_description = "Аватар"

    # Відображення повного імені в списку
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = "Повне ім'я"
    full_name_display.admin_order_field = 'first_name'  # для сортування
