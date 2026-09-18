"""Tests for role-based authorization and project-access hardening."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


@pytest.fixture
def tm(db):
    return User.objects.create_user(username="tim", password="secret")


@pytest.fixture
def pm(db):
    return User.objects.create_user(
        username="megan",
        password="secret",
        role=User.Role.PROJECT_MANAGER,
    )


def build_post_data(projects):
    """Build a POST payload submitting an On Track row for each project."""
    defaults = {
        "status": ProjectFeedback.Status.ON_TRACK,
        "completion": 50,
        "completed_work": "",
        "notes": "",
        "risks": "",
        "action_items": "",
    }
    data = {
        "form-TOTAL_FORMS": str(len(projects)),
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    for i, project in enumerate(projects):
        for key, value in {**defaults, "project": str(project.id)}.items():
            data[f"form-{i}-{key}"] = value
    return data


@pytest.mark.django_db
def test_dashboard_denied_for_team_member(client, tm):
    client.force_login(tm)
    assert client.get("/weekly/dashboard/").status_code == 403


@pytest.mark.django_db
def test_trends_denied_for_team_member(client, tm):
    client.force_login(tm)
    assert client.get("/weekly/trends/").status_code == 403


@pytest.mark.django_db
def test_dashboard_allowed_for_project_manager(client, pm):
    client.force_login(pm)
    assert client.get("/weekly/dashboard/").status_code == 200


@pytest.mark.django_db
def test_trends_allowed_for_project_manager(client, pm):
    project = Project.objects.create(name="Alpha")
    client.force_login(pm)
    response = client.get("/weekly/trends/")
    assert response.status_code == 200
    assert project.name in response.content.decode()


@pytest.mark.django_db
def test_dashboard_anonymous_redirects_to_login(client):
    response = client.get("/weekly/dashboard/")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
def test_weekly_form_still_open_to_team_members(client, tm):
    client.force_login(tm)
    assert client.get("/weekly/").status_code == 200


@pytest.mark.django_db
def test_cannot_report_feedback_for_unassigned_project(client, tm):
    assigned = Project.objects.create(name="Alpha")
    foreign = Project.objects.create(name="Foreign")
    tm.projects.add(assigned)

    client.force_login(tm)
    year, week = week_for_today()
    response = client.post(f"/weekly/?year={year}&week={week}", build_post_data([assigned, foreign]))
    assert response.status_code == 302

    report = WeeklyReport.objects.get(user=tm, year=year, week=week)
    reported_projects = set(report.feedbacks.values_list("project_id", flat=True))
    assert reported_projects == {assigned.id}
    assert not ProjectFeedback.objects.filter(project=foreign).exists()