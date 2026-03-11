from django import forms
from .models import Invoice

class InvoicePaymentForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['payment_link', 'payment_qr']
        widgets = {
            'payment_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional payment link (e.g. PayPal, Stripe)'}),
            'payment_qr': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
