"""View tests for authentication and the login flow."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project, ProjectFeedback, WeeklyReport
from projects.views import week_for_today

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="secret")


@pytest.mark.django_db
def test_unauthenticated_weekly_form_redirects_to_login(client):
    response = client.get("/weekly/")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
def test_unauthenticated_dashboard_redirects_to_login(client):
    response = client.get("/weekly/dashboard/")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
def test_authenticated_user_can_access_form(client, user):
    client.force_login(user)
    response = client.get("/weekly/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_access_dashboard(client, user):
    client.force_login(user)
    response = client.get("/weekly/dashboard/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert b"Sign in" in response.content


@pytest.mark.django_db
def test_valid_credentials_log_user_in(client, user):
    response = client.post(
        "/accounts/login/",
        {"username": "alice", "password": "secret"},
    )
    assert response.status_code == 302
    # The follow-up request to a protected view is now allowed.
    page = client.get("/weekly/")
    assert page.status_code == 200


@pytest.mark.django_db
def test_invalid_credentials_do_not_log_in(client, user):
    response = client.post(
        "/accounts/login/",
        {"username": "alice", "password": "wrong"},
    )
    assert response.status_code == 200
    assert b"did not match" in response.content
    assert client.get("/weekly/").status_code == 302


@pytest.mark.django_db
def test_logout_blocks_access_again(client, user):
    client.force_login(user)
    assert client.get("/weekly/").status_code == 200
    client.post("/accounts/logout/")
    assert client.get("/weekly/").status_code == 302