# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from unittest import skipIf

import django
from django.contrib.auth.models import User
from django.test import TestCase

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class AdminIndexIntegrationTests(TestCase):
    def setUp(self):
        self.superuser = User.objects._create_user(
            username='superuser', email='user@example.com', password='top_secret', is_staff=True, is_superuser=True)
        self.assertTrue(self.client.login(username=self.superuser.username, password='top_secret'))

        self.auth_app_list_url = reverse('admin:app_list', kwargs={'app_label': 'auth'})

    def test_app_groups_in_context(self):
        response = self.client.get(reverse('admin:index'))

        self.assertIn('dashboard_app_list', response.context)
        self.assertGreater(len(response.context['dashboard_app_list']), 0)

    def test_no_app_groups_in_context_outside_index(self):
        response = self.client.get(reverse('admin:auth_user_changelist'))

        self.assertNotIn('dashboard_app_list', response.context)

    @skipIf(django.VERSION < (1, 9), 'Django < 1.9 does not support template origins.')
    def test_app_groups_in_index(self):
        response = self.client.get(reverse('admin:index'))

        template_path = response.templates[0].origin.name.replace('\\', '/')
        self.assertTrue(template_path.endswith('django_admin_index/templates/admin/index.html'), template_path)

    def test_no_app_list_links_index(self):
        response = self.client.get(reverse('admin:index'))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_change_form(self):
        response = self.client.get(reverse('admin:auth_user_change', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_change_list(self):
        response = self.client.get(reverse('admin:auth_user_changelist'))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_delete_confirmation(self):
        response = self.client.get(reverse('admin:auth_user_delete', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_delete_selected_confirmation(self):
        response = self.client.post(reverse('admin:auth_user_changelist'), data={
            'action': 'delete_selected',
            'select_across': 0,
            'index': 0,
            '_selected_action': self.superuser.pk,
        })
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_object_history(self):
        response = self.client.get(reverse('admin:auth_user_history', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)
