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



