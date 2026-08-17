from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = "accounts"


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("account/", views.account, name="account"),
    path("profile/edit/", views.profile_edit, name="profile-edit"),
    path("admin/", views.admin_dashboard,name="admin-dashboard"),
    path(
    "admin/users/",
    views.admin_users,
    name="admin-users",
    ),
    path(
    "admin/users/<int:user_id>/toggle-active/",
    views.toggle_user_active,
    name="admin-toggle-user-active",
    ),
    path(
        "verify-email/<int:user_id>/<str:token>/",
        views.verify_email,
        name="verify-email",
    ),
    path(
        "verification-pending/",
        views.verification_pending,
        name="verification-pending",
    ),
    path(
    "password-reset/",
    auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset.html",
        email_template_name="accounts/password_reset_email.txt",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url="/accounts/password-reset/done/",
    ),
    name="password-reset",
),
path(
    "password-reset/done/",
    auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html",
    ),
    name="password-reset-done",
),
path(
    "password-reset/confirm/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url="/accounts/password-reset/complete/",
    ),
    name="password-reset-confirm",
),
path(
    "password-reset/complete/",
    auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html",
    ),
    name="password-reset-complete",
),
]