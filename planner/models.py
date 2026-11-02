### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Assignment(models.Model):
    """A single piece of coursework that belongs to one user."""

    class Priority(models.IntegerChoices):
        # Stored as integers so that ordering by priority sorts Low < Medium < High
        # instead of alphabetically.
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    title = models.CharField(max_length=200)
    course_name = models.CharField(max_length=100, help_text='e.g. INF601 - Advanced Programming in Python')
    description = models.TextField(blank=True)
    due_date = models.DateField()
    priority = models.PositiveSmallIntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    is_completed = models.BooleanField('completed', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Unfinished work first, soonest due date first, highest priority first.
        ordering = ['is_completed', 'due_date', '-priority']

    def __str__(self):
        return f'{self.title} ({self.course_name})'

    def get_absolute_url(self):
        return reverse('assignment_detail', args=[self.pk])

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.localdate()

    @property
    def days_until_due(self):
        """Days from today to the due date; negative once the date has passed."""
        return (self.due_date - timezone.localdate()).days
