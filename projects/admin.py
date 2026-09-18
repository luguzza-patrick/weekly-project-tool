"""Admin registrations for the core project models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Project, ProjectFeedback, User, WeeklyReport


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


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    """Admin for weekly reports."""

    list_display = ("user", "year", "week")
    list_select_related = ("user",)
    list_filter = ("year", "week")


@admin.register(ProjectFeedback)
class ProjectFeedbackAdmin(admin.ModelAdmin):
    """Admin for per-project feedback."""

    list_display = ("project", "status", "completion", "report")
    list_select_related = ("project", "report")
    list_filter = ("status",)
