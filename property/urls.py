from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_property_stock, name='property_stock_data'),
]
