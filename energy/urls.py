from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_energy_stock, name='energy_stock_data'),
]