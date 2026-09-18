"""Project-level views."""

from django.http import HttpResponse


def home(request):
    """Serve a simple home page so the app has a reachable root."""
    return HttpResponse("Weekly Project Tool")