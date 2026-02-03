from django.contrib import admin

from .models import KarmaHistory


@admin.register(KarmaHistory)
class KarmaHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False  # Тільки через signals
