# forex/admin.py
from django.contrib import admin
from django.utils.html import format_html
# Tambahkan import mark_safe jika diperlukan
from django.utils.safestring import mark_safe
from .models import ForexCandle 

@admin.register(ForexCandle)
class ForexCandleAdmin(admin.ModelAdmin):
    list_display = (
        'pair', 'timeframe', 'timestamp', 
        'open_price', 'high_price', 'low_price', 'close_price', 
        'candle_direction', 'volume'
    )
    list_filter = ('pair', 'timeframe', 'timestamp')
    search_fields = ('pair',)
    date_hierarchy = 'timestamp'
    list_per_page = 50

    # Custom column dengan indikator warna (menggunakan mark_safe untuk HTML statis)
    @admin.display(description='Trend')
    def candle_direction(self, obj):
        if obj.close_price > obj.open_price:
            # Bullish (Naik) - Warna Hijau
            return mark_safe('<span style="color: green; font-weight: bold;">▲ Bullish</span>')
        elif obj.close_price < obj.open_price:
            # Bearish (Turun) - Warna Merah
            return mark_safe('<span style="color: red; font-weight: bold;">▼ Bearish</span>')
        else:
            # Doji (Tetap) - Warna Abu-abu
            return mark_safe('<span style="color: gray; font-weight: bold;">■ Doji</span>')

    def has_add_permission(self, request):
        return False