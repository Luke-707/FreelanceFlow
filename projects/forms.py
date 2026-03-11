from django import forms
from .models import Project, Milestone, ProjectApplication
from django.contrib.auth import get_user_model

User = get_user_model()


class ClientProjectForm(forms.ModelForm):
    """Form used by clients to post a project (no freelancer selection)."""

    class Meta:
        model = Project
        fields = ['title', 'description', 'budget', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your project requirements in detail...'}),
            'budget': forms.NumberInput(attrs={'placeholder': 'e.g. 500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProjectApplicationForm(forms.ModelForm):
    """Form used by freelancers to apply for an open project."""

    class Meta:
        model = ProjectApplication
        fields = ['cover_letter', 'proposed_rate']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Briefly explain why you are a great fit for this project...', 'class': 'form-control'}),
            'proposed_rate': forms.NumberInput(attrs={'placeholder': 'Your proposed rate ($)', 'class': 'form-control'}),
        }


class PaymentSetupForm(forms.ModelForm):
    """Form used by freelancers to set a payment amount and payment details on their project."""

    class Meta:
        model = Project
        fields = ['payment_amount', 'payment_link', 'payment_qr']
        widgets = {
            'payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount to charge client ($)', 'step': '0.01'}),
            'payment_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Payment link (e.g. PayPal, Stripe)'}),
            'payment_qr': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class DeliverableUploadForm(forms.ModelForm):
    """Form used by freelancers to upload the finished project deliverable."""

    class Meta:
        model = Project
        fields = ['deliverable', 'deliverable_note', 'preview_image', 'preview_link']
        widgets = {
            'deliverable_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe what you have delivered...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'due_date', 'amount', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

