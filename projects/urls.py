"""URL routes for the projects app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.weekly_form, name="weekly"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("trends/", views.trends, name="trends"),
    path("notifications/", views.notifications, name="notifications"),
]