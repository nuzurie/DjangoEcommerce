from django import forms
from localflavor.ca.forms import CAProvinceSelect, CAPostalCodeField, CAProvinceField
from localflavor.us.forms import USStateField, USZipCodeField, USStateSelect

COUNTRY_CHOICES = (
    ('', 'Select Country'),
    ('CA', 'CANADA'),
    ('US', 'AMERICA'),
)

PAYMENT_CHOICE = (
    ('S', 'Credit or Debit'),
    ('P', 'PAYPAL'),
)


class CheckoutForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    street_address_1 = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "1234 Main St."
    }))
    apartment = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "Apartment or suite"
    }))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, widget=forms.Select(attrs={
        'onChange': 'countrySelect(this)',
        'class': 'custom-select d-block w-100',
    }))
    province = CAProvinceField(widget=CAProvinceSelect(attrs={
        'type': 'hidden',
        'class':'custom-select d-block w-100',
    }))
    ca_postal_code = CAPostalCodeField(required=False, widget=forms.TextInput(attrs={
        'class': 'custom-select d-block w-100',
    }))
    us_state = USStateField(widget=USStateSelect(attrs={
        'class': 'custom-select d-block w-100',
    }), required=False)
    us_zip_code = USZipCodeField(required=False, widget=forms.TextInput(attrs={
        'class': 'custom-select d-block w-100',
    }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(choices=PAYMENT_CHOICE, widget=forms.RadioSelect())

