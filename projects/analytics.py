"""Aggregation helpers for trend analysis and health indicators."""

from datetime import date, timedelta

from .models import Project, ProjectFeedback


def recent_weeks(num_weeks=8):
    """Return the last num_weeks as (year, week) ISO tuples ending this week."""
    current = date.today()
    weeks = []
    for offset in range(num_weeks - 1, -1, -1):
        year, week, _ = (current - timedelta(days=offset * 7)).isocalendar()
        weeks.append((year, week))
    return weeks


def week_label(year, week):
    """Human label for a reporting week, e.g. '2026-W38'."""
    return f"{year}-W{week:02d}"


def compute_trends(num_weeks=8):
    """Aggregate completion and status counts across recent reporting weeks."""
    weeks = recent_weeks(num_weeks)
    labels = [week_label(*w) for w in weeks]

    projects = list(Project.objects.order_by("name"))
    project_ids = [p.id for p in projects]

    week_feedbacks = _fetch_week_feedbacks(weeks)

    averages = []
    status_counts = []
    project_completion = {
        project_ids[i]: [None] * num_weeks for i in range(len(project_ids))
    }

    for index, (year, week) in enumerate(weeks):
        feedbacks = week_feedbacks.get((year, week), [])
        if feedbacks:
            averages.append(
                sum(fb.completion for fb in feedbacks) / len(feedbacks)
            )
        else:
            averages.append(None)

        status_counts.append(
            {
                status: sum(1 for fb in feedbacks if fb.status == status)
                for status in ProjectFeedback.Status.values
            }
        )

        for fb in feedbacks:
            idx = project_ids.index(fb.project_id) if fb.project_id in project_ids else None
            if idx is not None and project_completion[fb.project_id][index] is None:
                project_completion[fb.project_id][index] = fb.completion

    return {
        "weeks": weeks,
        "labels": labels,
        "averages": averages,
        "status_counts": status_counts,
        "projects": projects,
        "project_completion": project_completion,
    }


def _fetch_week_feedbacks(weeks):
    """Group all feedback for the given weeks by their (year, week)."""
    grouped = {}
    for year, week in weeks:
        feedbacks = ProjectFeedback.objects.filter(
            report__year=year, report__week=week
        ).select_related("report", "project")
        grouped[(year, week)] = list(feedbacks)
    return grouped


def health_indicators():
    """Return a current-health snapshot per project based on latest feedback."""
    indicators = []
    for project in Project.objects.order_by("name"):
        latest = (
            project.feedbacks.select_related("report")
            .order_by("-report__year", "-report__week")
            .first()
        )
        if latest is None:
            indicators.append(
                {
                    "project": project.name,
                    "indicator": "No data",
                    "status": None,
                    "completion": None,
                }
            )
        else:
            indicators.append(
                {
                    "project": project.name,
                    "indicator": latest.get_status_display(),
                    "status": latest.status,
                    "completion": latest.completion,
                }
            )
    return indicators