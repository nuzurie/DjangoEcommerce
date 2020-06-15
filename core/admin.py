from django.contrib import admin

from .models import Item, OrderItem, Order, ShippingDetails, StripePayment

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingDetails)
admin.site.register(StripePayment)
