"""Tests for notifications created for At Risk / Blocked projects."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Notification, Project, ProjectFeedback

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


def post_feedback(client, project, status, completion=40):
    """Submit the weekly form as the logged-in client, returning the response."""
    return client.post(
        "/weekly/",
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-project": str(project.id),
            "form-0-status": status,
            "form-0-completion": str(completion),
            "form-0-completed_work": "Done stuff",
            "form-0-notes": "",
            "form-0-risks": "",
            "form-0-action_items": "",
        },
    )


@pytest.mark.django_db
def test_reporting_at_risk_notifies_other_members(client, user):
    member = User.objects.create_user(username="bob", password="secret")
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    member.projects.add(project)
    client.force_login(user)

    post_feedback(client, project, ProjectFeedback.Status.AT_RISK)

    notes = Notification.objects.filter(recipient=member)
    assert notes.count() == 1
    assert "Alpha" in notes.first().message
    # The reporter is not notified for their own report.
    assert not Notification.objects.filter(recipient=user).exists()


@pytest.mark.django_db
def test_reporting_blocked_notifies_other_members(client, user):
    member = User.objects.create_user(username="bob", password="secret")
    project = Project.objects.create(name="Nova")
    user.projects.add(project)
    member.projects.add(project)
    client.force_login(user)

    post_feedback(client, project, ProjectFeedback.Status.BLOCKED)

    notes = Notification.objects.filter(recipient=member)
    assert notes.count() == 1
    assert "Nova" in notes.first().message


@pytest.mark.django_db
def test_reporting_on_track_creates_no_notification(client, user):
    member = User.objects.create_user(username="bob", password="secret")
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    member.projects.add(project)
    client.force_login(user)

    post_feedback(client, project, ProjectFeedback.Status.ON_TRACK)

    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_re_saving_same_status_does_not_duplicate_notification(client, user):
    member = User.objects.create_user(username="bob", password="secret")
    project = Project.objects.create(name="Alpha")
    user.projects.add(project)
    member.projects.add(project)
    client.force_login(user)

    post_feedback(client, project, ProjectFeedback.Status.BLOCKED)
    post_feedback(client, project, ProjectFeedback.Status.BLOCKED)

    assert Notification.objects.filter(recipient=member).count() == 1


@pytest.mark.django_db
def test_notifications_view_lists_only_own_notifications(client):
    reporter = User.objects.create_user(username="carol", password="secret")
    member = User.objects.create_user(username="bob", password="secret")
    non_member = User.objects.create_user(username="dave", password="secret")
    project = Project.objects.create(name="Beta")
    reporter.projects.add(project)
    member.projects.add(project)
    client.force_login(reporter)

    post_feedback(client, project, ProjectFeedback.Status.AT_RISK)

    # The member involved with the project can see the notification.
    client.force_login(member)
    response = client.get("/weekly/notifications/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Beta" in content
    assert "1 unread" in content

    # A user unrelated to the project is unaffected.
    client.force_login(non_member)
    assert client.get("/weekly/notifications/").status_code == 200