"""Template filters for styling the three simple project statuses."""

from django import template

from ..models import ProjectFeedback

register = template.Library()

_BADGE_CLASSES = {
    ProjectFeedback.Status.ON_TRACK: "text-bg-success",
    ProjectFeedback.Status.AT_RISK: "text-bg-warning",
    ProjectFeedback.Status.BLOCKED: "text-bg-danger",
}


@register.filter
def status_badge(value):
    """Return the Bootstrap badge colour class for a status value."""
    return _BADGE_CLASSES.get(str(value), "text-bg-secondary")