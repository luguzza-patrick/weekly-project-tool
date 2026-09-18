"""View tests for the weekly feedback form."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


def build_post_data(projects, fields=None):
    """Build a formset POST payload for the given projects."""
    fields = fields or {}
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
        overrides = fields.get(project.id, {})
        row = {**defaults, "project": str(project.id), **overrides}
        for key, value in row.items():
            data[f"form-{i}-{key}"] = value
    return data


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


@pytest.mark.django_db
def test_memberships_resolve_signed_in_users_projects(user):
    p1 = Project.objects.create(name="Alpha")
    p2 = Project.objects.create(name="Beta")
    user.projects.add(p1, p2)
    assert set(user.projects.all()) == {p1, p2}


@pytest.mark.django_db
def test_get_shows_week_header_and_project_inputs(client, user):
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    client.force_login(user)
    year, week = week_for_today()

    response = client.get("/weekly/")

    assert response.status_code == 200
    assert f"Week {week}, {year}".encode() in response.content
    assert b"Alpha" in response.content


@pytest.mark.django_db
def test_get_renders_one_input_row_per_project(client, user):
    p1 = Project.objects.create(name="Alpha")
    p2 = Project.objects.create(name="Beta")
    user.projects.add(p1, p2)
    client.force_login(user)

    response = client.get("/weekly/")
    content = response.content.decode()

    assert b"Alpha" in response.content
    assert b"Beta" in response.content
    assert content.count("<fieldset") == 2


@pytest.mark.django_db
def test_get_with_no_projects_shows_empty_form_not_error(client, user):
    client.force_login(user)

    response = client.get("/weekly/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "not assigned to any projects" in content
    assert "form-" not in content


@pytest.mark.django_db
def test_post_saves_one_feedback_per_project(client, user):
    p1 = Project.objects.create(name="Alpha")
    p2 = Project.objects.create(name="Beta")
    user.projects.add(p1, p2)
    client.force_login(user)
    year, week = week_for_today()

    data = build_post_data(
        [p1, p2],
        fields={
            p1.id: {"status": ProjectFeedback.Status.ON_TRACK, "completion": 80},
            p2.id: {"status": ProjectFeedback.Status.BLOCKED, "completion": 10},
        },
    )
    response = client.post("/weekly/", data)

    assert response.status_code == 302
    report = WeeklyReport.objects.get(user=user, year=year, week=week)
    assert report.feedbacks.count() == 2
    on_track = report.feedbacks.get(project=p1)
    blocked = report.feedbacks.get(project=p2)
    assert on_track.status == ProjectFeedback.Status.ON_TRACK
    assert on_track.completion == 80
    assert blocked.status == ProjectFeedback.Status.BLOCKED
    assert blocked.completion == 10


@pytest.mark.django_db
def test_editing_existing_report_prepopulates(client, user):
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    year, week = week_for_today()
    report = WeeklyReport.objects.create(user=user, year=year, week=week)
    ProjectFeedback.objects.create(
        report=report,
        project=project,
        status=ProjectFeedback.Status.AT_RISK,
        completion=60,
        notes="Close to done.",
    )
    client.force_login(user)

    response = client.get("/weekly/")

    content = response.content.decode()
    assert ProjectFeedback.Status.AT_RISK.encode() in response.content
    assert 'value="60"' in content
    assert "Close to done." in content


@pytest.mark.django_db
def test_post_redirect_on_invalid_submission_renders_form_again(client, user):
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    client.force_login(user)

    data = build_post_data([project], fields={project.id: {"completion": 101}})
    response = client.post("/weekly/", data)

    assert response.status_code == 200
    assert ProjectFeedback.objects.count() == 0