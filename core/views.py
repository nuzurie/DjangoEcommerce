from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import json
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import stripe
import json

from .models import Item, OrderItem, Order, ShippingDetails, StripePayment
from .forms import CheckoutForm


class HomeView(ListView):
    model = Item
    paginate_by = 18
    template_name = 'home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user,
                ordered=False
            )
            return render(self.request, 'order_summary.html', {
                'order': order,
            })
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order!")
            return redirect("/")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, ordered=False)[0]
        form = CheckoutForm()
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout-page.html', context)
    # TODO: Change redirect links for valid forms
    def post(self, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, ordered=False)[0]
        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            try:
                order = Order.objects.get(
                    user=self.request.user,
                    ordered=False
                )
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                street_address_1 = form.cleaned_data.get('street_address_1')
                apartment = form.cleaned_data.get('apartment')
                country = form.cleaned_data.get('country')
                province = form.cleaned_data.get('province')
                ca_postal_code = form.cleaned_data.get('ca_postal_code')
                us_state = form.cleaned_data.get('us_state')
                us_zip_code = form.cleaned_data.get('us_zip_code')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                if country == 'CA':
                    province_or_state = province
                    postal_or_zip_code = ca_postal_code
                else:
                    province_or_state = us_state
                    postal_or_zip_code = us_zip_code

                shipping_details = ShippingDetails(
                    user=self.request.user,
                    first_name=first_name,
                    last_name=last_name,
                    street_address_1=street_address_1,
                    apartment=apartment,
                    country=country,
                    province_or_state=province_or_state,
                    postal_or_zip_code=postal_or_zip_code
                )
                shipping_details.save()
                order.shipping_details = shipping_details
                order.save()
                return redirect('core:stripe-payment')
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order!")
                return redirect("/")
        return render(self.request, 'checkout-page.html', {
            'form': form,
            'order': order
        })

stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'


def generate_response(intent):
    if intent.status == 'succeeded':
        # Handle post-payment fulfillment
        return JsonResponse({'success': True})
    else:
        # Any other status would be unexpected, so error
        return JsonResponse({'error': 'Invalid PaymentIntent status'})


class PaymentView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order,
            }
            return render(self.request, 'stripe-test.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order!")
            return redirect('/')

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            byte_str = self.request.body
            data = json.loads(byte_str.decode('utf-8'))
            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                # Create the PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.get_order_total())*100,
                    currency='CAD',
                    payment_method=data["payment_method_id"],

                    # A PaymentIntent can be confirmed some time after creation,
                    # but here we want to confirm (collect payment) immediately.
                    confirm=True,

                    # If the payment requires any follow-up actions from the
                    # customer, like two-factor authentication, Stripe will error
                    # and you will need to prompt them for a new payment method.
                    error_on_requires_action=True,
                )
                id = intent['id']
                if intent['status'] == 'succeeded':
                    payment = StripePayment(
                        stripe_payment_id=id,
                        user=self.request.user,
                        amount=intent["amount"]
                    )
                    payment.save()
                    order.ordered = True
                    order.payment = payment
                    order.ordered_date = timezone.now()
                    order.save()
                    for order_item in order.items.all():
                        order_item.delete()
                    print("OH YES!")

                return generate_response(intent)
            except stripe.error.CardError as e:
                # Display error on client
                return json.dumps({'error': e.user_message}), 200





class ProductView(DetailView):
    model = Item
    template_name = 'product-page.html'


@login_required()
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item successfully added!")
        else:
            order.items.add(order_item)
            messages.info(request, "Item successfully added!")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item successfully added!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order.items.remove(order_item)
            order_item.delete()
            messages.success(request, "Item removed from your order!")
            return redirect('core:products', slug=slug)
        else:
            messages.warning(request, "Item is not in your cart!")
            return redirect('core:products', slug=slug)
    else:
        messages.danger(request, "You do not have an active order!")
        return redirect('core:products', slug=slug)

@login_required()
def remove_one_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.success(request, "Item quantity updated!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.warning(request, "Item is not in your cart!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        messages.danger(request, "You do not have an active order!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
