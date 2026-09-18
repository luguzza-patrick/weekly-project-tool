"""Project-level views."""

from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect, render

from projects.forms import SignUpForm
from projects.models import User


def home(request):
    """Serve a simple home page so the app has a reachable root."""
    return HttpResponse("Weekly Project Tool")


def signup(request):
    """Create a new Team Member account and log the user in."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.TEAM_MEMBER
            user.save()
            login(request, user)
            return redirect("weekly")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})