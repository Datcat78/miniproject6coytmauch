### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Accounts. Login and logout are Django's built-in views; after logging in
    # users go to LOGIN_REDIRECT_URL (the dashboard), after logging out to
    # LOGOUT_REDIRECT_URL (home). LogoutView only accepts POST.
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
         name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/new/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.assignment_update, name='assignment_update'),
    path('assignments/<int:pk>/toggle/', views.assignment_toggle_complete, name='assignment_toggle_complete'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
]
