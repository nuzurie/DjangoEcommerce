from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
import decimal


CATEGORY_CHOICES = (
    ('S', 'Shirts'),
    ('SW', 'Sports Wear'),
    ('OW', 'Outer Wear'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100)
    label = models.CharField(choices=LABEL_CHOICES, max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=300)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:products', kwargs={
            'slug': self.slug,
        })

    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart(self):
        return reverse('core:remove-from-cart', kwargs={
            'slug': self.slug
        })

    def cross_sells(self):
        from core.models import Order, OrderItem
        order_qs = Order.objects.filter(items__item=self)
        order_item_qs = OrderItem.objects.filter(order__in=order_qs)
        items_qs = Item.objects.filter(orderitem__in=order_item_qs).distinct()
        return items_qs


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        if self.item.discount_price:
            return self.item.discount_price * self.quantity
        return self.item.price * self.quantity

    def get_total_saving(self):
        if self.item.discount_price:
            total_saving = decimal.Decimal('0.00')
            total_saving += (self.item.price - self.item.discount_price)*self.quantity
            return total_saving


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_details = models.ForeignKey('ShippingDetails', on_delete=models.SET_NULL,null=True, blank=True)
    payment = models.ForeignKey('StripePayment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def quantity(self):
        return sum([item.quantity for item in self.items.filter(user=self.user, ordered=False)])

    def get_order_total(self):
        total = decimal.Decimal('0.00')
        for item in self.items.all():
            total += (item.get_total_price())
        return total


COUNTRY_CHOICES = (
    ('CA', 'CANADA'),
    ('US', 'AMERICA'),
)

PAYMENT_CHOICE = (
    ('S', 'Stripe'),
    ('P', 'PAYPAL'),
)


class ShippingDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    street_address_1 = models.CharField(max_length=100)
    apartment = models.CharField(max_length=12, null=True, blank=True)
    country = models.CharField(choices=COUNTRY_CHOICES, max_length=3)
    province_or_state = models.CharField(max_length=24, null=True, blank=True)
    postal_or_zip_code = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return self.user.username


class StripePayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    stripe_payment_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



