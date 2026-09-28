from django.contrib import admin
from .models import FinanceStock

@admin.register(FinanceStock)
class FinanceStockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'date', 'open_price', 'close_price', 'volume')
    list_filter = ('ticker',)
    search_fields = ('ticker',)