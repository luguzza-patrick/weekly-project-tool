"""Tests for the seed_demo management command."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from projects.models import Project, ProjectFeedback, WeeklyReport

User = get_user_model()


@pytest.mark.django_db
def test_seed_demo_creates_expected_rows():
    call_command("seed_demo")

    assert User.objects.filter(username__in=["alice", "bob", "carol"]).count() == 3
    alice = User.objects.get(username="alice")
    assert alice.role == User.Role.PROJECT_MANAGER
    assert alice.projects.count() == 3
    assert Project.objects.count() == 3
    assert WeeklyReport.objects.count() == 2  # alice and bob, one current week each
    assert ProjectFeedback.objects.count() == 5  # 3 for alice, 2 for bob


@pytest.mark.django_db
def test_seed_demo_is_idempotent():
    call_command("seed_demo")
    user_count = User.objects.count()
    project_count = Project.objects.count()
    report_count = WeeklyReport.objects.count()
    feedback_count = ProjectFeedback.objects.count()

    call_command("seed_demo")

    assert User.objects.count() == user_count
    assert Project.objects.count() == project_count
    assert WeeklyReport.objects.count() == report_count
    assert ProjectFeedback.objects.count() == feedback_count


@pytest.mark.django_db
def test_seed_demo_feedback_covers_all_statuses():
    call_command("seed_demo")

    statuses = set(
        ProjectFeedback.objects.values_list("status", flat=True).distinct()
    )
    assert ProjectFeedback.Status.ON_TRACK in statuses
    assert ProjectFeedback.Status.AT_RISK in statuses
    assert ProjectFeedback.Status.BLOCKED in statuses