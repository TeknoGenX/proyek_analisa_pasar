# Django URL Configuration for Market Hub
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # Halaman Utama Portal
    path('', views.home_view, name='home'),
    
    # Universal Interactive Dashboard Saham (semua sektor)
    path('dashboard/<str:ticker>/', views.stock_dashboard_view, name='stock_dashboard'),
    
    # Live Yahoo Finance Sync
    path('sync/<str:ticker>/', views.sync_ticker_view, name='sync_ticker'),
    
    # Fitur Komparasi Multi-Emiten
    path('compare/', views.compare_view, name='stock_compare'),
    
    # Ekspor Data (CSV & Excel)
    path('export/<str:ticker>/csv/', views.export_csv_view, name='export_csv'),
    path('export/<str:ticker>/excel/', views.export_excel_view, name='export_excel'),
    
    # Watchlist Pribadi & Notifikasi Sinyal
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/toggle/<str:ticker>/', views.toggle_watchlist_view, name='toggle_watchlist'),
    
    # Dokumentasi REST API (Swagger UI & OpenAPI JSON)
    path('api/docs/', views.swagger_docs_view, name='swagger_docs'),
    path('api/openapi.json', views.openapi_spec_view, name='openapi_spec'),
    
    # Admin Panel (Gunakan admin.site.urls langsung)
    path('admin/', admin.site.urls),
    
    # Endpoint API untuk masing-masing sektor / modul
    path('api/forex/', include('forex.urls')),
    path('api/transport/', include('transport.urls')),
    path('api/basic-idn/', include('basic_idn.urls')),
    path('api/cyclical/', include('cyclical.urls')),
    path('api/property/', include('property.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/energy/', include('energy.urls')),
    path('api/industrial/', include('industrial.urls')),
    path('api/non-cyclical/', include('non_cyclical.urls')),
    path('api/infrastructure/', include('infrastructure.urls')),
    path('api/health/', include('health.urls')),
    path('api/technology/', include('technology.urls')),
]