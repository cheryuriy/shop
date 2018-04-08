from django import forms

class ImageFieldForm(forms.Form):
    files = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True})) # widget=forms.ClearableFileInput(attrs={'multiple': True})
