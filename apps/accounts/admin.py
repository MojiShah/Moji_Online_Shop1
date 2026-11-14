
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    model = CustomUser

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    ordering = ("email",)

    list_display = (
        "email",
        "phone_number",
        "is_active",
        "is_staff",
        "is_phone_verified",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_phone_verified",
        "is_email_verified",
    )

    search_fields = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("Authentication", {
            "fields": (
                "email",
                "password",
            )
        }),

        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
            )
        }),

        ("Verification", {
            "fields": (
                "is_email_verified",
                "is_phone_verified",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),

            "fields": (
                "email",
                "first_name",
                "last_name",
                "phone_number",
                "password1",
                "password2",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
