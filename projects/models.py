"""Core models: the project user (with a role) and projects."""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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

    projects = models.ManyToManyField(
        "Project",
        blank=True,
        related_name="members",
        help_text="Projects the user is involved in.",
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


class WeeklyReport(models.Model):
    """One user's weekly feedback report tying their per-project rows together."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="weekly_reports",
        help_text="The user who is reporting for this week.",
    )
    year = models.PositiveIntegerField(help_text="Reporting year, e.g. 2026.")
    week = models.PositiveIntegerField(
        help_text="Reporting week number within the year (1-53)."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "year", "week"],
                name="unique_user_year_week",
            )
        ]
        ordering = ["-year", "-week"]

    def __str__(self):
        return f"#{self.week} {self.year} - {self.user}"


class ProjectFeedback(models.Model):
    """Per-project feedback recorded against a weekly report."""

    class Status(models.TextChoices):
        ON_TRACK = "on_track", "On Track"
        AT_RISK = "at_risk", "At Risk"
        BLOCKED = "blocked", "Blocked"

    report = models.ForeignKey(
        WeeklyReport,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        help_text="The weekly report this feedback belongs to.",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        help_text="The project this feedback is about.",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        help_text="Simple status: On Track, At Risk, or Blocked.",
    )
    completion = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Estimated completion percentage (0-100).",
    )
    completed_work = models.TextField(
        blank=True, help_text="What was completed this week."
    )
    notes = models.TextField(blank=True, help_text="Short notes on the project.")
    risks = models.TextField(
        blank=True, help_text="Current risks and blockers."
    )
    action_items = models.TextField(
        blank=True, help_text="Action items / next steps."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["report", "project"],
                name="unique_feedback_per_report_project",
            )
        ]
        ordering = ["project__name"]

    def clean(self):
        """Reject an invalid status value even when saved via the ORM."""
        super().clean()
        if self.status not in ProjectFeedback.Status.values:
            raise ValidationError(
                {"status": f"'{self.status}' is not a valid status."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project} - {self.get_status_display()}"