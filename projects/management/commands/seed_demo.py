"""Seed the app with realistic demo data for quick internal review."""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project, ProjectFeedback, WeeklyReport

User = get_user_model()

DEMO_PASSWORD = "demo-password"

PROJECTS = [
    ("Phoenix", "Re-launch of the customer portal with a modern dashboard."),
    ("Atlas", "Consolidate reporting across the four business units."),
    ("Nova", "Migrate the data warehouse to the new pipeline."),
]

FEEDBACK = {
    "Phoenix": {
        "status": ProjectFeedback.Status.ON_TRACK,
        "completion": 65,
        "completed_work": "Shipped the new login screen and updated onboarding.",
        "notes": "Testing on track.",
        "risks": "None.",
        "action_items": "UAT review on Friday.",
    },
    "Atlas": {
        "status": ProjectFeedback.Status.AT_RISK,
        "completion": 40,
        "completed_work": "Scoped the data model for the report portal.",
        "notes": "Awaiting sign-off on two dashboards.",
        "risks": "Missing finance stakeholder availability.",
        "action_items": "Book a review with finance this week.",
    },
    "Nova": {
        "status": ProjectFeedback.Status.BLOCKED,
        "completion": 20,
        "completed_work": "Provisioned the new staging environment.",
        "notes": "Stuck on vendor data access.",
        "risks": "Vendor has not delivered the export API key.",
        "action_items": "Escalate access request to procurement.",
    },
}


class Command(BaseCommand):
    """Create demo users, projects, and a current-week report with feedback."""

    help = "Seed the app with realistic demo data for internal review."

    def handle(self, *args, **options):
        users = self.seed_users()
        projects = self.seed_projects()
        self.seed_memberships(users, projects)
        self.seed_reports_and_feedback(users, projects)
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def get_or_create_user(self, username, role, first_name=None, email=""):
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(
                username=username,
                password=DEMO_PASSWORD,
                first_name=first_name or username,
                email=email,
            )
        user.role = role
        user.save()
        return user

    def seed_users(self):
        alice = self.get_or_create_user(
            "alice",
            User.Role.PROJECT_MANAGER,
            first_name="Alice",
            email="alice@example.com",
        )
        bob = self.get_or_create_user(
            "bob", User.Role.TEAM_MEMBER, first_name="Bob"
        )
        carol = self.get_or_create_user(
            "carol", User.Role.TEAM_MEMBER, first_name="Carol"
        )
        return {"alice": alice, "bob": bob, "carol": carol}

    def seed_projects(self):
        projects = {}
        for name, description in PROJECTS:
            project, _ = Project.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            projects[name] = project
        return projects

    def seed_memberships(self, users, projects):
        users["alice"].projects.add(*projects.values())
        users["bob"].projects.add(projects["Phoenix"], projects["Atlas"])
        users["carol"].projects.add(projects["Atlas"], projects["Nova"])

    def seed_reports_and_feedback(self, users, projects):
        year, week, _ = date.today().isocalendar()
        for name, data in FEEDBACK.items():
            project = projects[name]
            report, _ = WeeklyReport.objects.get_or_create(
                user=users["alice"], year=year, week=week
            )
            ProjectFeedback.objects.get_or_create(
                report=report, project=project, defaults=data
            )
            if name in ("Phoenix", "Atlas"):
                bob_report, _ = WeeklyReport.objects.get_or_create(
                    user=users["bob"], year=year, week=week
                )
                ProjectFeedback.objects.get_or_create(
                    report=bob_report, project=project, defaults=data
                )