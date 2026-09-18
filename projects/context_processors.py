"""Template context processors for the projects app."""


def notification_count(request):
    """Expose the unread notification count for the navbar badge."""
    count = 0
    if request.user.is_authenticated:
        count = request.user.notifications.filter(read=False).count()
    return {"unread_notifications": count}