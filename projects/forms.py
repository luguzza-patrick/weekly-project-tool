"""Forms used by the weekly feedback form."""

from django import forms
from django.forms import formset_factory

from .models import Project, ProjectFeedback

FEEDBACK_FIELDS = (
    "status",
    "completion",
    "completed_work",
    "notes",
    "risks",
    "action_items",
)


class ProjectFeedbackForm(forms.Form):
    """One row of per-project feedback inside the weekly form."""

    project = forms.ModelChoiceField(
        queryset=Project.objects.all(), widget=forms.HiddenInput()
    )
    status = forms.ChoiceField(choices=ProjectFeedback.Status.choices)
    completion = forms.IntegerField(
        min_value=0, max_value=100, initial=0, label="Progress (%)"
    )
    completed_work = forms.CharField(
        required=False, widget=forms.Textarea, label="Completed work"
    )
    notes = forms.CharField(required=False, widget=forms.Textarea, label="Notes")
    risks = forms.CharField(required=False, widget=forms.Textarea, label="Risks / blockers")
    action_items = forms.CharField(
        required=False, widget=forms.Textarea, label="Action items / next steps"
    )


ProjectFeedbackFormSet = formset_factory(ProjectFeedbackForm, extra=0)