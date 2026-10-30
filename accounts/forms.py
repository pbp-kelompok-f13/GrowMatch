from django import forms
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(
                attrs={"autocomplete": "email", "placeholder": "you@example.com"}
            ),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if email and (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "This email is already used by another account."
            )
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["location", "bio"]
        widgets = {
            "location": forms.TextInput(
                attrs={"placeholder": "e.g. Depok, Indonesia"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us a little about your gardening journey",
                }
            ),
        }