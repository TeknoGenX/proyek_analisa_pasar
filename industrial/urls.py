from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_industrial_stock, name='industrial_stock_data'),
]
