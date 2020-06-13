from django.contrib import admin

from .models import Item, OrderItem, Order, ShippingDetails

admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingDetails)
