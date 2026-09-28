from django.urls import path
from . import views

urlpatterns = [
    path('<str:ticker>/', views.get_finance_stock, name='finance_stock_data'),
]