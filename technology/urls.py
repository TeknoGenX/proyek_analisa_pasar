from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_technology_stock, name='technology_stock_data'),
]
