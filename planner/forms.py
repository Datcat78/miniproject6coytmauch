### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Assignment


class BootstrapFormMixin:
    """Gives every field the Bootstrap 5 CSS class for its widget type and
    outlines fields in red when they fail validation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            widget.attrs.setdefault('class', css_class)

    def is_valid(self):
        valid = super().is_valid()
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} is-invalid".strip()
        return valid


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    """Django's built-in registration form (username + password twice),
    styled for Bootstrap. Passwords are checked against AUTH_PASSWORD_VALIDATORS."""


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Django's built-in login form, styled for Bootstrap."""


class AssignmentForm(BootstrapFormMixin, forms.ModelForm):
    """Form for creating an assignment.

    The owner is deliberately left out of the fields: the view sets it to the
    logged-in user, so a user can never create an assignment for someone else.
    """

    class Meta:
        model = Assignment
        fields = ['title', 'course_name', 'description', 'due_date', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'autofocus': True}),
            'description': forms.Textarea(attrs={'rows': 4}),
            # type="date" shows the browser's date picker, which expects YYYY-MM-DD.
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
