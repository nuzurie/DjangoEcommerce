from django.urls import path

from .views import (
    HomeView,
    checkout,
    ProductView,
    add_to_cart,
    remove_from_cart,
    )


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view() , name='item-list'),
    path('checkout', checkout, name='checkout'),
    path('products/<slug>', ProductView.as_view(), name='products'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remvove-to-cart/<slug>', remove_from_cart, name='remove-from-cart'),
]