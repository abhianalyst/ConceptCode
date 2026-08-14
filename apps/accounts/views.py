from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import Profile
from .services.email_verification import send_verification_email


User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.create(user=user)

            send_verification_email(request, user)

            return redirect("accounts:verification-pending")
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def verification_pending(request):
    return render(
        request,
        "accounts/verification_pending.html",
    )


def verify_email(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return render(
            request,
            "accounts/email_verification_failed.html",
            {"message": "Invalid verification link."},
            status=400,
        )

    if user.email_verified:
        return render(
            request,
            "accounts/email_verification_failed.html",
            {"message": "This email address has already been verified."},
            status=400,
        )

    if not default_token_generator.check_token(user, token):
        return render(
            request,
            "accounts/email_verification_failed.html",
            {"message": "This verification link is invalid or has expired."},
            status=400,
        )

    user.email_verified = True
    user.save(update_fields=["email_verified"])

    return render(
        request,
        "accounts/email_verified.html",
    )
