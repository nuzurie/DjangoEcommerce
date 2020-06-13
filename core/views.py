from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DetailView, ListView, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Item, OrderItem, Order, ShippingDetails
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
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order!")
                return redirect("/")
        return render(self.request, 'checkout-page.html', {
            'form': form,
            'order': order
        })


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
