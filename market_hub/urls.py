# market_hub/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoint API / Web untuk masing-masing sektor
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