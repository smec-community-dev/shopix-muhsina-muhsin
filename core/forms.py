from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

class CustomPasswordResetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)

        if not users.exists():
            raise forms.ValidationError("No user found with this email.")

        for user in users:
            if user.is_staff or user.is_superuser:
                raise forms.ValidationError(
                    "Admins must reset password via admin panel."
                )

        return email