from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_infrastructure_stock, name='infrastructure_stock_data'),
]
