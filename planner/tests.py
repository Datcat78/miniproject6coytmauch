### INF601 - Advanced Programming in Python
### Coyt Mauch
### Mini Project 6

import re
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment

User = get_user_model()


def make_password():
    """A random password for throwaway test users, so none is hardcoded."""
    return secrets.token_urlsafe(16)


def make_assignment(owner, title, days_from_today=7, **kwargs):
    return Assignment.objects.create(
        owner=owner,
        title=title,
        course_name='INF601',
        due_date=timezone.localdate() + timedelta(days=days_from_today),
        **kwargs,
    )


def logged_in_user_id(client):
    return client.session.get('_auth_user_id')


class RegistrationTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_successful_registration_logs_user_in_and_redirects_to_dashboard(self):
        password = make_password()
        response = self.client.post(reverse('register'), {
            'username': 'newstudent', 'password1': password, 'password2': password,
        })
        self.assertRedirects(response, reverse('dashboard'))
        user = User.objects.get(username='newstudent')
        self.assertEqual(logged_in_user_id(self.client), str(user.pk))

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(reverse('register'), {
            'username': 'newstudent', 'password1': make_password(), 'password2': make_password(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='newstudent').exists())

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user('taken', password=make_password())
        password = make_password()
        response = self.client.post(reverse('register'), {
            'username': 'taken', 'password1': password, 'password2': password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors)
        self.assertEqual(User.objects.filter(username='taken').count(), 1)

    def test_logged_in_user_is_redirected_away_from_register(self):
        self.client.force_login(User.objects.create_user('alice', password=make_password()))
        self.assertRedirects(self.client.get(reverse('register')), reverse('dashboard'))


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.password = make_password()
        self.user = User.objects.create_user('alice', password=self.password)

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {'username': 'alice', 'password': self.password})
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(logged_in_user_id(self.client), str(self.user.pk))

    def test_login_returns_user_to_the_page_they_asked_for(self):
        url = reverse('assignment_list')
        response = self.client.post(reverse('login'), {
            'username': 'alice', 'password': self.password, 'next': url,
        })
        self.assertRedirects(response, url)

    def test_wrong_password_shows_error_and_does_not_log_in(self):
        response = self.client.post(reverse('login'), {'username': 'alice', 'password': 'not-' + self.password})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertIsNone(logged_in_user_id(self.client))

    def test_logged_in_user_visiting_login_goes_to_dashboard(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse('login')), reverse('dashboard'))

    def test_logout_rejects_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(logged_in_user_id(self.client), str(self.user.pk))

    def test_logout_post_logs_out_and_redirects_home(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertIsNone(logged_in_user_id(self.client))


class LoginRequiredTests(TestCase):
    def test_public_pages_load_without_logging_in(self):
        for name in ['home', 'about', 'login', 'register']:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_assignment_pages_redirect_anonymous_users_to_login(self):
        assignment = make_assignment(User.objects.create_user('owner', password=make_password()), 'Essay')
        urls = [
            reverse('dashboard'),
            reverse('assignment_list'),
            reverse('assignment_create'),
            reverse('assignment_detail', args=[assignment.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_anonymous_post_cannot_create_an_assignment(self):
        self.client.post(reverse('assignment_create'), {
            'title': 'Sneaky', 'course_name': 'X', 'due_date': timezone.localdate().isoformat(), 'priority': 2,
        })
        self.assertFalse(Assignment.objects.exists())


class OwnershipTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password=make_password())
        self.bob = User.objects.create_user('bob', password=make_password())
        self.alice_assignment = make_assignment(self.alice, 'Alice homework')
        self.bob_assignment = make_assignment(self.bob, 'Bob homework', days_from_today=-1)
        self.client.force_login(self.alice)

    def test_list_shows_only_own_assignments(self):
        for status in ['', 'active', 'completed', 'overdue']:
            with self.subTest(status=status or 'all'):
                response = self.client.get(reverse('assignment_list'), {'status': status} if status else {})
                self.assertNotContains(response, 'Bob homework')
                self.assertTrue(all(a.owner == self.alice for a in response.context['assignments']))
        self.assertContains(self.client.get(reverse('assignment_list')), 'Alice homework')

    def test_dashboard_counts_only_own_assignments(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['total'], 1)
        # Bob's assignment is overdue; it must not show up in Alice's overdue list.
        self.assertEqual(len(response.context['overdue']), 0)
        self.assertNotContains(response, 'Bob homework')

    def test_own_assignment_detail_loads(self):
        response = self.client.get(reverse('assignment_detail', args=[self.alice_assignment.pk]))
        self.assertContains(response, 'Alice homework')

    def test_another_users_assignment_returns_404(self):
        response = self.client.get(reverse('assignment_detail', args=[self.bob_assignment.pk]))
        self.assertEqual(response.status_code, 404)

    def test_new_assignment_belongs_to_logged_in_user_even_if_another_owner_is_posted(self):
        response = self.client.post(reverse('assignment_create'), {
            'owner': self.bob.pk,  # not a form field, so it must be ignored
            'title': 'New essay',
            'course_name': 'ENG101',
            'due_date': timezone.localdate().isoformat(),
            'priority': Assignment.Priority.HIGH,
        })
        assignment = Assignment.objects.get(title='New essay')
        self.assertEqual(assignment.owner, self.alice)
        self.assertRedirects(response, reverse('assignment_detail', args=[assignment.pk]))


class DeleteAssignmentTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password=make_password())
        self.bob = User.objects.create_user('bob', password=make_password())
        self.assignment = make_assignment(self.alice, 'Alice homework')
        self.delete_url = reverse('assignment_delete', args=[self.assignment.pk])

    def test_detail_page_has_delete_button_and_confirmation_modal(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse('assignment_detail', args=[self.assignment.pk]))
        self.assertContains(response, 'data-bs-toggle="modal" data-bs-target="#deleteModal"')
        self.assertContains(response, 'id="deleteModal"')
        self.assertContains(response, 'data-bs-dismiss="modal">Cancel</button>')
        self.assertContains(response, 'Confirm Delete')
        self.assertContains(response, f'<form method="post" action="{self.delete_url}">')

    def test_owner_can_delete_and_is_redirected_to_list(self):
        self.client.force_login(self.alice)
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, reverse('assignment_list'))
        self.assertContains(response, 'Deleted &quot;Alice homework&quot;.')
        self.assertFalse(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_modal_form_submits_with_a_valid_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.alice)
        page = client.get(reverse('assignment_detail', args=[self.assignment.pk])).content.decode()
        modal = page[page.index('id="deleteModal"'):]
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', modal).group(1)

        self.assertEqual(client.post(self.delete_url).status_code, 403)  # no token -> rejected
        self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())

        response = client.post(self.delete_url, {'csrfmiddlewaretoken': token})
        self.assertRedirects(response, reverse('assignment_list'))
        self.assertFalse(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_get_request_does_not_delete(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)
        self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_other_user_cannot_delete(self):
        self.client.force_login(self.bob)
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)
        self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())

    def test_anonymous_user_cannot_delete(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.delete_url}", fetch_redirect_response=False)
        self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())
