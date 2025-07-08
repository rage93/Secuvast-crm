from django import forms
from django.contrib.auth.models import User
from .models import Company

PLAN_CHOICES = (
    ("free", "Free"),
    ("pro", "Pro"),
)

class CompanySignupForm(forms.Form):
    company_name = forms.CharField(max_length=255)
    subdomain = forms.SlugField()
    plan = forms.ChoiceField(choices=PLAN_CHOICES)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_subdomain(self):
        subdomain = self.cleaned_data["subdomain"]
        if Company.objects.filter(slug_subdomain=subdomain).exists():
            raise forms.ValidationError("Subdomain already taken")
        return subdomain

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned
