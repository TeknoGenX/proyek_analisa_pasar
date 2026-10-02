#forex/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<str:pair>/', views.get_forex_pair, name='forex_pair_data'),
]