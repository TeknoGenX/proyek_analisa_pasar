from django.contrib import admin
from .models import ForexData

@admin.register(ForexData)
class ForexDataAdmin(admin.ModelAdmin):
    # Kolom yang akan ditampilkan di tabel admin
    list_display = ('pair', 'timestamp', 'bid_price', 'ask_price', 'volume')
    # Filter sidebar berdasarkan pasangan mata uang
    list_filter = ('pair',)
    # Kolom pencarian
    search_fields = ('pair',)