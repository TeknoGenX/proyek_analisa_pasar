from django.urls import path
from . import views

urlpatterns = [
    # Endpoint WEB (merender HTML) ditaruh di awal agar tidak tertimpa path parameter generik
    path('web/<str:ticker>/', views.finance_web_dashboard, name='finance_web_dashboard'),
    
    # Endpoint API (mengembalikan JSON)
    path('<str:ticker>/', views.get_finance_stock, name='finance_stock_data'),
]