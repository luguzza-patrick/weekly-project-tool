"""Admin registrations for the core project models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Project, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin for the custom user, exposing the role field."""

    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Role",
            {
                "fields": ("role",),
            },
        ),
    )
    list_display = ("username", "email", "role", "is_staff")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for projects."""

    list_display = ("name", "owner")
    list_select_related = ("owner",)
