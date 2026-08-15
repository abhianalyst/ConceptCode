from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegistrationForm
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

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                email=email,
                password=password,
            )

            if user is None:
                form.add_error(
                    None,
                    "Invalid email or password.",
                )
            elif not user.email_verified:
                form.add_error(
                    None,
                    "Please verify your email address before logging in.",
                )
            else:
                login(request, user)

                return redirect("core:home")
    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )

def logout_view(request):
    logout(request)

    return redirect("core:account")

@login_required
def account(request):
    return render(
        request,
        "accounts/account.html",
        {"user": request.user},
    )