"""Views for the weekly feedback tool."""

from datetime import date

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .analytics import compute_trends, health_indicators
from .forms import ProjectFeedbackFormSet
from .models import Notification, ProjectFeedback, User, WeeklyReport


def week_for_today():
    """Return the (year, week) of the reporting period (ISO week)."""
    year, week, _ = date.today().isocalendar()
    return year, week


def project_manager_required(func):
    """Allow only Project Managers (authenticated users with the PM role).

    Anonymous users are still redirected to the login page; other signed-in
    users (e.g. Team Members) are denied with HTTP 403.
    """

    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.PROJECT_MANAGER:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper


def resolve_week(request):
    """Return the (year, week) to display, from query params or today's week."""
    default_year, default_week = week_for_today()
    try:
        year = int(request.GET.get("year", default_year))
        week = int(request.GET.get("week", default_week))
    except (TypeError, ValueError):
        return default_year, default_week
    if not 1 <= week <= 53 or year < 1:
        return default_year, default_week
    return year, week


def week_jump_url(name, year, week):
    """Return the named URL rendering the given week."""
    if (year, week) == week_for_today():
        return f"/{name}/"
    return f"/{name}/?year={year}&week={week}"


def initial_for_projects(projects, report):
    """Build the empty-form initial data for each project's feedback row."""
    existing = {}
    if report is not None:
        existing = {fb.project_id: fb for fb in report.feedbacks.all()}

    def value(project, field, fallback):
        fb = existing.get(project.id)
        return getattr(fb, field) if fb is not None else fallback

    return [
        {
            "project": project.id,
            "status": value(project, "status", ProjectFeedback.Status.ON_TRACK),
            "completion": value(project, "completion", 0),
            "completed_work": value(project, "completed_work", ""),
            "notes": value(project, "notes", ""),
            "risks": value(project, "risks", ""),
            "action_items": value(project, "action_items", ""),
        }
        for project in projects
    ]


def save_feedback(request, year, week, formset):
    """Persist each valid form as one ProjectFeedback for this report + project.

    Only feedback for projects the user is assigned to is saved; any form rows
    that reference a project outside the user's own projects are skipped.
    """
    allowed_projects = set(request.user.projects.values_list("id", flat=True))
    report, _ = WeeklyReport.objects.get_or_create(
        user=request.user, year=year, week=week
    )
    for form in formset.forms:
        data = form.cleaned_data
        feedback_project_id = data["project"].id
        if feedback_project_id not in allowed_projects:
            continue
        feedback = ProjectFeedback.objects.filter(
            report=report, project=data["project"]
        ).first()
        if feedback is None:
            feedback = ProjectFeedback(report=report, project=data["project"])
        previous_status = feedback.status if feedback.pk else None
        feedback.status = data["status"]
        feedback.completion = data["completion"]
        feedback.completed_work = data["completed_work"]
        feedback.notes = data["notes"]
        feedback.risks = data["risks"]
        feedback.action_items = data["action_items"]
        feedback.save()
        if _should_notify(previous_status, feedback):
            create_notifications(feedback)


def _should_notify(previous_status, feedback):
    """True when a project just transitioned to At Risk or Blocked."""
    alerted = (
        feedback.status == ProjectFeedback.Status.AT_RISK
        or feedback.status == ProjectFeedback.Status.BLOCKED
    )
    return alerted and feedback.status != previous_status


def create_notifications(feedback):
    """Alert project members (other than the reporter) about a risky project."""
    members = feedback.project.members.exclude(pk=feedback.report.user_id)
    message = (
        f"{feedback.project.name} was reported "
        f"{feedback.get_status_display()} (week {feedback.report.week}, "
        f"{feedback.report.year})."
    )
    Notification.objects.bulk_create(
        Notification(recipient=member, project=feedback.project, message=message)
        for member in members
    )


@login_required
def weekly_form(request):
    """Render and process the weekly feedback form for the signed-in user."""
    user = request.user
    projects = user.projects.all() if user.is_authenticated else user.projects.none()
    year, week = resolve_week(request)

    if request.method == "POST":
        formset = ProjectFeedbackFormSet(request.POST)
        if formset.is_valid():
            save_feedback(request, year, week, formset)
            return redirect(week_jump_url("weekly", year, week))
    else:
        report = WeeklyReport.objects.filter(
            user=user, year=year, week=week
        ).first()
        formset = ProjectFeedbackFormSet(
            initial=initial_for_projects(projects, report)
        )

    context = {
        "formset": formset,
        "rows": list(zip(projects, formset.forms)),
        "year": year,
        "week": week,
    }
    return render(request, "projects/weekly_form.html", context)


@project_manager_required
def trends(request):
    """Show progress/status trends and health indicators across recent weeks."""
    data = compute_trends()
    context = {
        "labels": data["labels"],
        "averages": data["averages"],
        "status_counts": data["status_counts"],
        "projects": data["projects"],
        "project_completion": data["project_completion"],
        "health": health_indicators(),
    }
    return render(request, "projects/trends.html", context)


@login_required
def notifications(request):
    """Show the signed-in user's notifications about project status."""
    notes = request.user.notifications.all()
    context = {
        "notifications": notes,
        "unread": notes.filter(read=False).count(),
    }
    return render(request, "projects/notifications.html", context)


@project_manager_required
def dashboard(request):
    """Show feedback across projects for a chosen reporting week."""
    year, week = resolve_week(request)
    reports = WeeklyReport.objects.filter(year=year, week=week)
    feedbacks = ProjectFeedback.objects.filter(report__in=reports).select_related(
        "report__user", "project"
    )

    counts = {
        ProjectFeedback.Status.ON_TRACK: feedbacks.filter(
            status=ProjectFeedback.Status.ON_TRACK
        ).count(),
        ProjectFeedback.Status.AT_RISK: feedbacks.filter(
            status=ProjectFeedback.Status.AT_RISK
        ).count(),
        ProjectFeedback.Status.BLOCKED: feedbacks.filter(
            status=ProjectFeedback.Status.BLOCKED
        ).count(),
    }

    context = {
        "feedbacks": feedbacks,
        "counts": counts,
        "year": year,
        "week": week,
        "total": feedbacks.count(),
    }
    return render(request, "projects/dashboard.html", context)