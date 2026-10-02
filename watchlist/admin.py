from django.contrib import admin
from .models import WatchlistItem

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'sector', 'user', 'session_key', 'target_price', 'created_at')
    list_filter = ('sector', 'created_at')
    search_fields = ('ticker', 'notes')
