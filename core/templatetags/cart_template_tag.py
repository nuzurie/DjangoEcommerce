from django import template
from core.models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        q = Order.objects.filter(user=user, ordered=False)
        if q.exists():
            return q[0].quantity()
    return 0
