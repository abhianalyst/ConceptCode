from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from PIL import Image


User = get_user_model()


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "full_name",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
    )


class ProfileForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
    )

    phone_number = forms.CharField(
        max_length=20,
        required=False,
    )

    profile_picture = forms.ImageField(
        required=False,
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.profile = profile

        if user is not None:
            self.fields["full_name"].initial = user.full_name

        if profile is not None:
            self.fields["phone_number"].initial = profile.phone_number

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()

        if not full_name:
            raise forms.ValidationError(
                "Full name is required."
            )

        return full_name

    def clean_phone_number(self):
        return self.cleaned_data["phone_number"].strip()

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get("profile_picture")

        if not profile_picture:
            return profile_picture

        max_size = 5 * 1024 * 1024

        if profile_picture.size > max_size:
            raise forms.ValidationError(
                "Profile picture must be 5 MB or smaller."
            )

        try:
            image = Image.open(profile_picture)
            image.verify()

            profile_picture.seek(0)

            image = Image.open(profile_picture)
            image_format = image.format

            if image_format not in ("JPEG", "PNG"):
                raise forms.ValidationError(
                    "Profile picture must be a JPEG or PNG image."
                )

            profile_picture.seek(0)

        except forms.ValidationError:
            raise

        except Exception:
            raise forms.ValidationError(
                "Please upload a valid image file."
            )

        return profile_picture