"""Core models: the project user (with a role) and projects."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A user with a role distinguishing Project Managers from Team Members."""

    class Role(models.TextChoices):
        PROJECT_MANAGER = "PM", "Project Manager"
        TEAM_MEMBER = "TM", "Team Member"

    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.TEAM_MEMBER,
        help_text="Whether the user is a Project Manager or a Team Member.",
    )


class Project(models.Model):
    """A project that team members and managers report weekly feedback on."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_projects",
        help_text="Optional project manager responsible for the project.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name