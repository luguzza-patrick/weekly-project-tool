"""Model tests for the core models: the user role and Project."""

import pytest
from django.contrib.auth import get_user_model

from projects.models import Project

User = get_user_model()


@pytest.mark.django_db
def test_default_user_role_is_team_member():
    user = User.objects.create_user(username="alice", password="secret")
    assert user.role == User.Role.TEAM_MEMBER


@pytest.mark.django_db
def test_user_can_be_a_project_manager():
    user = User.objects.create_user(
        username="bob",
        password="secret",
        role=User.Role.PROJECT_MANAGER,
    )
    assert user.role == User.Role.PROJECT_MANAGER


@pytest.mark.django_db
def test_create_project():
    owner = User.objects.create_user(username="owner", password="secret")
    project = Project.objects.create(
        name="Alpha",
        description="Launch the new portal.",
        owner=owner,
    )
    assert project.name == "Alpha"
    assert project.description == "Launch the new portal."
    assert project.owner == owner


@pytest.mark.django_db
def test_project_owner_is_optional():
    project = Project.objects.create(name="Solo")
    assert project.owner is None


@pytest.mark.django_db
def test_project_string_representation():
    project = Project.objects.create(name="Beta")
    assert str(project) == "Beta"