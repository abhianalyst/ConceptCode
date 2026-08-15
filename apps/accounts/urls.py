from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
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
]