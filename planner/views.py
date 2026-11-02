### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AssignmentForm, SignUpForm
from .models import Assignment

# (value used in ?status=, label shown on the tab)
STATUS_FILTERS = [
    ('all', 'All'),
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('overdue', 'Overdue'),
]


def home(request):
    return render(request, 'planner/home.html')


def about(request):
    return render(request, 'planner/about.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user in right away instead of making them log in again.
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    # Every query starts from the current user's assignments only.
    mine = Assignment.objects.filter(owner=request.user)
    stats = mine.aggregate(
        total=Count('pk'),
        completed=Count('pk', filter=Q(is_completed=True)),
    )
    active = mine.filter(is_completed=False)

    context = {
        'total': stats['total'],
        'completed': stats['completed'],
        'active': stats['total'] - stats['completed'],
        'percent_complete': round(stats['completed'] * 100 / stats['total']) if stats['total'] else 0,
        'overdue': active.filter(due_date__lt=today),
        'due_soon': active.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7)),
    }
    return render(request, 'planner/dashboard.html', context)


@login_required
def assignment_list(request):
    status = request.GET.get('status', 'all')
    assignments = Assignment.objects.filter(owner=request.user)

    if status == 'active':
        assignments = assignments.filter(is_completed=False)
    elif status == 'completed':
        assignments = assignments.filter(is_completed=True)
    elif status == 'overdue':
        assignments = assignments.filter(is_completed=False, due_date__lt=timezone.localdate())
    else:
        status = 'all'

    context = {
        'assignments': assignments,
        'status': status,
        'status_filters': STATUS_FILTERS,
    }
    return render(request, 'planner/assignment_list.html', context)


@login_required
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.owner = request.user
            assignment.save()
            messages.success(request, f'Added "{assignment.title}".')
            return redirect(assignment)
    else:
        form = AssignmentForm()
    return render(request, 'planner/assignment_form.html', {'form': form})


@login_required
def assignment_detail(request, pk):
    # Filtering on owner means another user's assignment returns 404, the same
    # as one that doesn't exist, so IDs can't be probed.
    assignment = get_object_or_404(Assignment, pk=pk, owner=request.user)
    return render(request, 'planner/assignment_detail.html', {'assignment': assignment})


@login_required
@require_POST
def assignment_delete(request, pk):
    # POST only (a GET returns 405), so a link or prefetch can never delete
    # anything; the request must come from the modal's CSRF-protected form.
    # The owner filter means another user's assignment returns 404 untouched.
    assignment = get_object_or_404(Assignment, pk=pk, owner=request.user)
    title = assignment.title
    assignment.delete()
    messages.success(request, f'Deleted "{title}".')
    return redirect('assignment_list')
