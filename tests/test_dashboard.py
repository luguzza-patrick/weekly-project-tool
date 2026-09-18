"""View tests for the dashboard."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


@pytest.mark.django_db
def test_dashboard_lists_feedback_rows(client, user):
    project = Project.objects.create(name="Alpha")
    year, week = week_for_today()
    report = WeeklyReport.objects.create(user=user, year=year, week=week)
    ProjectFeedback.objects.create(
        report=report,
        project=project,
        status=ProjectFeedback.Status.AT_RISK,
        completion=40,
        completed_work="Started migration.",
        risks="Dependency lag.",
        action_items="Upgrade library.",
    )

    client.force_login(user)
    response = client.get("/weekly/dashboard/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Alpha" in content
    assert "At Risk" in content
    assert "40%" in content
    assert "Started migration." in content
    assert "Dependency lag." in content
    assert "Upgrade library." in content
    assert user.get_username() in content


@pytest.mark.django_db
def test_dashboard_counts_match_rows(client, user):
    p1 = Project.objects.create(name="Alpha")
    p2 = Project.objects.create(name="Beta")
    p3 = Project.objects.create(name="Gamma")
    year, week = week_for_today()
    report = WeeklyReport.objects.create(user=user, year=year, week=week)
    statuses = [
        ProjectFeedback.Status.ON_TRACK,
        ProjectFeedback.Status.AT_RISK,
        ProjectFeedback.Status.BLOCKED,
    ]
    for project, status in zip([p1, p2, p3], statuses):
        ProjectFeedback.objects.create(report=report, project=project, status=status)

    client.force_login(user)
    response = client.get("/weekly/dashboard/")

    content = response.content.decode()
    assert "On Track: 1" in content
    assert "At Risk: 1" in content
    assert "Blocked: 1" in content


@pytest.mark.django_db
def test_dashboard_shows_empty_state_with_no_feedback(client, user):
    client.force_login(user)
    response = client.get("/weekly/dashboard/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "No feedback has been submitted" in content
    assert "On Track: 0" in content
    assert "At Risk: 0" in content
    assert "Blocked: 0" in content


@pytest.mark.django_db
def test_dashboard_only_includes_current_week(client, user, db):
    project = Project.objects.create(name="Alpha")
    year, week = week_for_today()
    current_report = WeeklyReport.objects.create(
        user=user, year=year, week=week
    )
    past_year, past_week = (year, week - 1) if week > 1 else (year - 1, 53)
    old_report = WeeklyReport.objects.create(
        user=user, year=past_year, week=past_week
    )
    ProjectFeedback.objects.create(
        report=current_report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
    )
    ProjectFeedback.objects.create(
        report=old_report,
        project=project,
        status=ProjectFeedback.Status.BLOCKED,
    )

    client.force_login(user)
    response = client.get("/weekly/dashboard/")

    content = response.content.decode()
    assert "On Track: 1" in content
    assert "Blocked: 0" in content