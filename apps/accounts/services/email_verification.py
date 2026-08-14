from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse


def generate_verification_token(user):
    return default_token_generator.make_token(user)


def build_verification_url(request, user, token):
    verification_path = reverse(
        "accounts:verify-email",
        kwargs={
            "user_id": user.pk,
            "token": token,
        },
    )

    return request.build_absolute_uri(verification_path)


def send_verification_email(request, user):
    token = generate_verification_token(user)
    verification_url = build_verification_url(request, user, token)

    send_mail(
        subject="Verify your ConceptCode email",
        message=(
            "Welcome to ConceptCode.\n\n"
            "Please verify your email address by visiting this link:\n\n"
            f"{verification_url}\n\n"
            "If you did not create this account, you can ignore this email."
        ),
        from_email="noreply@conceptcode.local",
        recipient_list=[user.email],
    )
