from django.urls import path

from .views import HomeView, checkout, ProductView


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view() , name='item-list'),
    path('checkout', checkout, name='checkout'),
    path('products/<slug:slug>', ProductView.as_view(), name='products'),
]