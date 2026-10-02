from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_cyclical_stock, name='cyclical_stock_data'),
]
