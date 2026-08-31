from django.test import TestCase

from apps.accounts.forms import ProfileForm

from django.test import SimpleTestCase

from .forms import LoginForm, RegistrationForm

# Create your tests here.
class BootstrapFormTests(TestCase):

    def test_login_form_uses_bootstrap_widgets(self):
        form = LoginForm()

        self.assertIn(
            "form-control",
            form.fields["email"].widget.attrs["class"],
        )

        self.assertIn(
            "form-control",
            form.fields["password"].widget.attrs["class"],
        )

    def test_registration_form_uses_bootstrap_widgets(self):
        form = RegistrationForm()

        self.assertIn(
            "form-control",
            form.fields["email"].widget.attrs["class"],
        )

        self.assertIn(
            "form-control",
            form.fields["full_name"].widget.attrs["class"],
        )

        self.assertIn(
            "form-control",
            form.fields["password1"].widget.attrs["class"],
        )

        self.assertIn(
            "form-control",
            form.fields["password2"].widget.attrs["class"],
        )

    def test_profile_form_uses_bootstrap_widgets(self):
        form = ProfileForm()

        for field_name in (
            "full_name",
            "phone_number",
            "profile_picture",
        ):
            self.assertIn(
                "form-control",
                form.fields[field_name].widget.attrs["class"],
            )