from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_health_stock, name='health_stock_data'),
]
