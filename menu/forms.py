from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "phone", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.Textarea(attrs={"rows": 4, "placeholder": "Delivery address"}),
        }
