from django import forms


class CompanySignupForm(forms.Form):
    """Simple form to capture company details from an authenticated user."""

    company_name = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields["company_name"]
        field.widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": field.label,
                "autofocus": True,
            }
        )
