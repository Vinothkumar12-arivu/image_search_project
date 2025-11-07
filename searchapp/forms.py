from django import forms
from .models import UploadedFile

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={
        'placeholder': 'Type a word that appears inside an image',
        'class': 'form-control',
    }))

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

class SearchForm(forms.Form):        # <-- NEW
    q = forms.CharField(max_length=255, required=False, label='Search')
