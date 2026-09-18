"""Model tests for the weekly feedback data model (weekly report + project feedback)."""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from projects.models import Project, ProjectFeedback, WeeklyReport

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


@pytest.fixture
def report(user):
    return WeeklyReport.objects.create(user=user, year=2026, week=38)


@pytest.fixture
def project(db):
    return Project.objects.create(name="Alpha")


@pytest.mark.django_db
def test_create_weekly_report(user):
    report = WeeklyReport.objects.create(user=user, year=2026, week=38)
    assert report.user == user
    assert (report.year, report.week) == (2026, 38)


@pytest.mark.django_db
def test_report_cannot_be_duplicated_for_same_user_and_week(user):
    WeeklyReport.objects.create(user=user, year=2026, week=38)
    with pytest.raises(IntegrityError):
        WeeklyReport.objects.create(user=user, year=2026, week=38)


@pytest.mark.django_db
def test_create_project_feedback(report, project):
    feedback = ProjectFeedback.objects.create(
        report=report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
        completion=75,
        completed_work="Shipped v1.",
        notes="Going well.",
        risks="None.",
        action_items="Draft docs.",
    )
    assert feedback.report == report
    assert feedback.project == project
    assert feedback.status == ProjectFeedback.Status.ON_TRACK
    assert feedback.completion == 75
    assert feedback.completed_work == "Shipped v1."


@pytest.mark.django_db
def test_status_choices_are_the_three_simple_values():
    assert set(ProjectFeedback.Status.values) == {"on_track", "at_risk", "blocked"}
    assert set(ProjectFeedback.Status.choices) == {
        (ProjectFeedback.Status.ON_TRACK, "On Track"),
        (ProjectFeedback.Status.AT_RISK, "At Risk"),
        (ProjectFeedback.Status.BLOCKED, "Blocked"),
    }


@pytest.mark.django_db
def test_valid_status_is_accepted(report, project):
    feedback = ProjectFeedback(
        report=report,
        project=project,
        status=ProjectFeedback.Status.BLOCKED,
    )
    feedback.save()
    assert feedback.status == ProjectFeedback.Status.BLOCKED


@pytest.mark.django_db
def test_invalid_status_is_rejected(report, project):
    feedback = ProjectFeedback(
        report=report,
        project=project,
        status="maybe",
    )
    with pytest.raises(ValidationError):
        feedback.save()


@pytest.mark.django_db
def test_completion_outside_0_100_is_rejected(report, project):
    feedback = ProjectFeedback(
        report=report,
        project=project,
        status=ProjectFeedback.Status.ON_TRACK,
        completion=150,
    )
    with pytest.raises(ValidationError):
        feedback.save()


@pytest.mark.django_db
def test_no_duplicate_feedback_for_same_report_and_project(report, project):
    ProjectFeedback.objects.create(
        report=report, project=project, status=ProjectFeedback.Status.ON_TRACK
    )
    # full_clean() in save() catches the duplicate before the database does.
    duplicate = ProjectFeedback(
        report=report, project=project, status=ProjectFeedback.Status.AT_RISK
    )
    with pytest.raises(ValidationError):
        duplicate.save()