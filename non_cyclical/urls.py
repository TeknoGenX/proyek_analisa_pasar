from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_non_cyclical_stock, name='non_cyclical_stock_data'),
]
