"""Tests for trend analysis and health indicators."""

import pytest
from django.contrib.auth import get_user_model

from projects.analytics import compute_trends, health_indicators, recent_weeks
from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


def previous_week(year, week):
    if week > 1:
        return year, week - 1
    return year - 1, 53


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice",
        password="secret",
        role=User.Role.PROJECT_MANAGER,
    )


@pytest.fixture
def project(db):
    return Project.objects.create(name="Alpha")


@pytest.mark.django_db
def test_recent_weeks_builds_ordered_list():
    weeks = recent_weeks(4)
    assert len(weeks) == 4
    assert weeks[-1] == week_for_today()


@pytest.mark.django_db
def test_compute_trends_aggregates_completion_and_status_counts(db, user, project):
    current_year, current_week = week_for_today()
    past_year, past_week = previous_week(current_year, current_week)

    current_report = WeeklyReport.objects.create(
        user=user, year=current_year, week=current_week
    )
    ProjectFeedback.objects.create(
        report=current_report,
        project=project,
        status=ProjectFeedback.Status.AT_RISK,
        completion=50,
    )

    past_report = WeeklyReport.objects.create(
        user=user, year=past_year, week=past_week
    )
    ProjectFeedback.objects.create(
        report=past_report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
        completion=20,
    )

    trends = compute_trends(8)
    current_index = trends["labels"].index(f"{current_year}-W{current_week:02d}")
    past_index = trends["labels"].index(f"{past_year}-W{past_week:02d}")

    assert trends["averages"][current_index] == 50
    assert trends["status_counts"][current_index]["at_risk"] == 1
    assert trends["status_counts"][current_index]["on_track"] == 0

    assert trends["project_completion"][project.id][current_index] == 50
    assert trends["project_completion"][project.id][past_index] == 20


@pytest.mark.django_db
def test_compute_trends_empty_week_has_none_average(db, user, project):
    trends = compute_trends(4)
    assert trends["averages"][-1] is None
    assert trends["status_counts"][-1]["at_risk"] == 0


@pytest.mark.django_db
def test_health_indicators_uses_latest_feedback(db, user, project):
    current_year, current_week = week_for_today()
    past_year, past_week = previous_week(current_year, current_week)

    past_report = WeeklyReport.objects.create(
        user=user, year=past_year, week=past_week
    )
    ProjectFeedback.objects.create(
        report=past_report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
        completion=90,
    )
    current_report = WeeklyReport.objects.create(
        user=user, year=current_year, week=current_week
    )
    ProjectFeedback.objects.create(
        report=current_report,
        project=project,
        status=ProjectFeedback.Status.BLOCKED,
        completion=40,
    )

    indicators = health_indicators()
    assert len(indicators) == 1
    assert indicators[0]["indicator"] == "Blocked"
    assert indicators[0]["status"] == ProjectFeedback.Status.BLOCKED
    assert indicators[0]["completion"] == 40


@pytest.mark.django_db
def test_trends_page_renders(client, user, project):
    client.force_login(user)
    response = client.get("/weekly/trends/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Trends" in content
    assert project.name in content
    assert "Project health" in content