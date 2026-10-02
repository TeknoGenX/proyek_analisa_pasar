from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_transport_stock, name='transport_stock_data'),
]
