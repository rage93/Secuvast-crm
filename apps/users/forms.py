from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from apps.users.models import Profile, ROLE_CHOICES


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ("user", "role", "avatar", "company")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["placeholder"] = field.label
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["required"] = False


class QuillFieldForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio",)


class TenantUserCreationForm(forms.ModelForm):
    """Form to create users inside a tenant company."""

    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, company=None, **kwargs):
        self.company = company
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("placeholder", field.label)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match")
        if self.company:
            from apps.companies.plans import PLAN_LIMITS
            limit = PLAN_LIMITS.get(self.company.plan, {}).get("users")
            if limit is not None and self.company.profiles.count() >= limit:
                raise forms.ValidationError("User limit reached for this plan")
        return cleaned

    def save(self, company):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data["password1"],
        )
        user.refresh_from_db()
        profile = user.profile
        profile.company = company
        profile.role = self.cleaned_data["role"]
        profile.save()
        return user


class InviteUserForm(forms.Form):
    """Collect email and role to invite a user."""

    email = forms.EmailField()
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("placeholder", field.label)

