"""Forms used by the weekly feedback tool."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import formset_factory

from .models import Project, ProjectFeedback, User

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
    status = forms.ChoiceField(
        choices=ProjectFeedback.Status.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    completion = forms.IntegerField(
        min_value=0,
        max_value=100,
        initial=0,
        label="Progress (%)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    completed_work = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Completed work",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Notes",
    )
    risks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Risks / blockers",
    )
    action_items = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Action items / next steps",
    )


ProjectFeedbackFormSet = formset_factory(ProjectFeedbackForm, extra=0)


class LoginForm(AuthenticationForm):
    """Authentication form with Bootstrap-styled inputs."""

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class SignUpForm(UserCreationForm):
    """Self-service account creation, bootstrapped, defaulting to Team Member."""

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")