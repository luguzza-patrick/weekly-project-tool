"""Template filters used by the projects app."""

from django.template import Library

register = Library()


@register.filter
def lookup(mapping, key):
    """Return mapping[key] or an empty list when missing."""
    return mapping.get(key, [])