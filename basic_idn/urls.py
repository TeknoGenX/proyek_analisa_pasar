from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_basic_stock, name='basic_stock_data'),
]
