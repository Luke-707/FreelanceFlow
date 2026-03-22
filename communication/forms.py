from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type a message...'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control', 'title': 'Attach a file'}),
        }
