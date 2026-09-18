"""Tests for self-service registration and password reset."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

User = get_user_model()

PASSWORD_SET_DATA = {
    "new_password1": "brand-new-password",
    "new_password2": "brand-new-password",
}


@pytest.mark.django_db
def test_signup_page_renders(client):
    response = client.get("/accounts/register/")
    assert response.status_code == 200
    assert b"Create an account" in response.content


@pytest.mark.django_db
def test_signup_creates_user_and_logs_in(client):
    response = client.post(
        "/accounts/register/",
        {
            "username": "newbie",
            "email": "newbie@example.com",
            "password1": "a-good-password",
            "password2": "a-good-password",
        },
    )
    assert response.status_code == 302
    # Redirects to the protected weekly form, so the user is now logged in.
    page = client.get("/weekly/")
    assert page.status_code == 200

    user = User.objects.get(username="newbie")
    assert user.role == User.Role.TEAM_MEMBER
    assert user.check_password("a-good-password")


@pytest.mark.django_db
def test_signup_rejects_mismatched_passwords(client):
    response = client.post(
        "/accounts/register/",
        {
            "username": "newbie",
            "email": "newbie@example.com",
            "password1": "aaaa",
            "password2": "bbbb",
        },
    )
    assert response.status_code == 200
    assert not User.objects.filter(username="newbie").exists()


@pytest.mark.django_db
def test_password_reset_sends_email_and_updates_password(client):
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="old-password"
    )

    response = client.post(
        "/accounts/password-reset/", {"email": "alice@example.com"}
    )
    assert response.status_code == 302
    assert len(mail.outbox) == 1

    body = mail.outbox[0].body
    match = re.search(r"(http://[^ ]+/reset/[^\s/]+/[^\s/]+)/?", body)
    assert match, "reset link not found in email"
    reset_url = match.group(1)

    reset_page = client.get(reset_url, follow=True)
    assert reset_page.status_code == 200
    assert "Choose a new password" in reset_page.content.decode()

    done = client.post(f"{reset_url}/", PASSWORD_SET_DATA)
    assert done.status_code == 302
    # Django's two-step flow redirects the first POST to the set-password URL,
    # where the actual new password is submitted.
    final = client.post(done.get("Location"), PASSWORD_SET_DATA)
    assert final.status_code == 302

    user.refresh_from_db()
    assert user.check_password("brand-new-password")

    # The new password works for a normal login.
    login_ok = client.login(username="alice", password="brand-new-password")
    assert login_ok is True


@pytest.mark.django_db
def test_password_reset_unknown_email_still_renders_done(client):
    response = client.post("/accounts/password-reset/", {"email": "nope@example.com"})
    assert response.status_code == 302
    assert len(mail.outbox) == 0