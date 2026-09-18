"""URL routes for the projects app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.weekly_form, name="weekly"),
]