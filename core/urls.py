from django.urls import path

from .views import (
    HomeView,
    CheckoutView,
    OrderSummaryView,
    ProductView,
    add_to_cart,
    remove_from_cart,
    remove_one_from_cart,
    PaymentView,
    )


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summar/y', OrderSummaryView.as_view(), name='order-summary'),
    path('products/<slug>', ProductView.as_view(), name='products'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remvove-to-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('remvove-one-from-cart/<slug>', remove_one_from_cart, name='remove-one-from-cart'),
    path('payment/', PaymentView.as_view(), name='stripe-payment'),

]