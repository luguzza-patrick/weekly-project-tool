"""Tests for week navigation and reviewing past weeks."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


def previous_week():
    year, week = week_for_today()
    if week > 1:
        return year, week - 1
    return year - 1, 53


@pytest.mark.django_db
def test_week_picker_renders_on_weekly_form(client, user):
    client.force_login(user)
    response = client.get("/weekly/")
    assert response.status_code == 200
    assert "Current week" in response.content.decode()
    assert 'name="year"' in response.content.decode()
    assert 'name="week"' in response.content.decode()


@pytest.mark.django_db
def test_week_picker_renders_on_dashboard(client, user):
    client.force_login(user)
    response = client.get("/weekly/dashboard/")
    assert response.status_code == 200
    assert "Current week" in response.content.decode()


@pytest.mark.django_db
def test_dashboard_switches_to_requested_week(client, user):
    client.force_login(user)
    project = Project.objects.create(name="Alpha")
    past_year, past_week = previous_week()
    report = WeeklyReport.objects.create(
        user=user, year=past_year, week=past_week
    )
    ProjectFeedback.objects.create(
        report=report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
        completion=80,
        completed_work="Old quarter work",
    )

    current = client.get("/weekly/dashboard/").content.decode()
    assert "Old quarter work" not in current

    past = client.get(
        f"/weekly/dashboard/?year={past_year}&week={past_week}"
    ).content.decode()
    assert "Old quarter work" in past
    assert "80%" in past
    assert "On Track: 1" in past


@pytest.mark.django_db
def test_dashboard_empty_week_shows_empty_state(client, user):
    client.force_login(user)
    year, week = previous_week()
    response = client.get(f"/weekly/dashboard/?year={year}&week={week}")
    assert response.status_code == 200
    content = response.content.decode()
    assert "No feedback has been submitted" in content
    assert "On Track: 0" in content


@pytest.mark.django_db
def test_weekly_form_prepopulates_past_week(client, user):
    client.force_login(user)
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    past_year, past_week = previous_week()
    report = WeeklyReport.objects.create(
        user=user, year=past_year, week=past_week
    )
    ProjectFeedback.objects.create(
        report=report,
        project=project,
        status=ProjectFeedback.Status.BLOCKED,
        completion=15,
        completed_work="Kicked off discovery",
    )

    response = client.get(f"/weekly/?year={past_year}&week={past_week}")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Kicked off discovery" in content
    assert "Blocked" in content
    assert "15" in content


@pytest.mark.django_db
def test_invalid_week_falls_back_to_current(client, user):
    client.force_login(user)
    year, week = week_for_today()
    current_week_page = client.get("/weekly/").content
    invalid = client.get("/weekly/?year=abc&week=xyz").content
    assert invalid == current_week_page
    # Out-of-range week also falls back.
    assert f"Week {week}, {year}".encode() in invalid