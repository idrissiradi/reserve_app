from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import NewUserChangeForm, NewUserCreationForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = NewUserCreationForm
    form = NewUserChangeForm
    model = User
    list_display = (
        "email",
        "admin",
        "is_active",
    )
    list_filter = (
        "email",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
