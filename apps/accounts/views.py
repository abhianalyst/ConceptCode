from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import Profile
from .services.email_verification import send_verification_email
from .permissions import admin_required
from django.db.models import Count

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

    return redirect("accounts:login")

@login_required
def account(request):
    return render(
        request,
        "accounts/account.html",
        {"user": request.user},
    )
@login_required
def profile_edit(request):
    profile = get_object_or_404(
        Profile,
        user=request.user,
    )

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            user=request.user,
            profile=profile,
        )

        if form.is_valid():
            request.user.full_name = form.cleaned_data["full_name"]
            request.user.save(update_fields=["full_name"])

            profile.phone_number = form.cleaned_data["phone_number"]

            profile_picture = form.cleaned_data.get("profile_picture")

            if profile_picture:
                profile.profile_picture = profile_picture

            profile.save()

            return redirect("accounts:account")
    else:
        form = ProfileForm(
            user=request.user,
            profile=profile,
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "profile": profile,
        },
    )

@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_students = User.objects.filter(
        role=User.Role.STUDENT
    ).count()
    total_admins = User.objects.filter(
        role=User.Role.ADMIN
    ).count()
    active_users = User.objects.filter(
        is_active=True
    ).count()

    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "total_users": total_users,
            "total_students": total_students,
            "total_admins": total_admins,
            "active_users": active_users,
        },
    )

@admin_required
def admin_users(request):
    users = User.objects.all().order_by("email")

    search_query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        users = users.filter(
            email__icontains=search_query
        ) | users.filter(
            full_name__icontains=search_query
        )

    if role_filter in {
        User.Role.STUDENT,
        User.Role.ADMIN,
    }:
        users = users.filter(role=role_filter)

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    return render(
        request,
        "accounts/admin_users.html",
        {
            "users": users,
            "search_query": search_query,
            "role_filter": role_filter,
            "status_filter": status_filter,
        },
    )

@admin_required
def toggle_user_active(request, user_id):
    if request.method != "POST":
        return redirect("accounts:admin-users")

    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        return redirect("accounts:admin-users")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    return redirect("accounts:admin-users")