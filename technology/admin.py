from django.contrib import admin
from .models import TechnologyStock

@admin.register(TechnologyStock)
class TechnologyStockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'date', 'open_price', 'close_price', 'volume')
    list_filter = ('ticker',)
    search_fields = ('ticker',)
