from django.contrib import admin

from .models import Profile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "role",
        "email_verified",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "email_verified",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "full_name",
    )

    ordering = (
        "email",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
    )

    search_fields = (
        "user__email",
        "user__full_name",
        "phone_number",
    )

    ordering = (
        "user__email",
    )