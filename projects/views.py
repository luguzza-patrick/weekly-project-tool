"""Views for the weekly feedback tool."""

from datetime import date

from django.shortcuts import redirect, render

from .forms import ProjectFeedbackFormSet
from .models import ProjectFeedback, WeeklyReport


def week_for_today():
    """Return the (year, week) of the reporting period (ISO week)."""
    year, week, _ = date.today().isocalendar()
    return year, week


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
    """Persist each valid form as one ProjectFeedback for this report + project."""
    report, _ = WeeklyReport.objects.get_or_create(
        user=request.user, year=year, week=week
    )
    for form in formset.forms:
        data = form.cleaned_data
        feedback = ProjectFeedback.objects.filter(
            report=report, project=data["project"]
        ).first()
        if feedback is None:
            feedback = ProjectFeedback(report=report, project=data["project"])
        feedback.status = data["status"]
        feedback.completion = data["completion"]
        feedback.completed_work = data["completed_work"]
        feedback.notes = data["notes"]
        feedback.risks = data["risks"]
        feedback.action_items = data["action_items"]
        feedback.save()


def weekly_form(request):
    """Render and process the weekly feedback form for the signed-in user."""
    user = request.user
    projects = user.projects.all() if user.is_authenticated else user.projects.none()
    year, week = week_for_today()

    if request.method == "POST":
        formset = ProjectFeedbackFormSet(request.POST)
        if formset.is_valid():
            save_feedback(request, year, week, formset)
            return redirect("weekly")
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


def dashboard(request):
    """Show all current-week feedback across projects with status counts."""
    year, week = week_for_today()
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