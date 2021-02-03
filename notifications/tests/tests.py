'''
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
'''
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines,missing-docstring
import json

import pytz

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.utils.timezone import localtime, utc
from notifications.base.models import notify_handler
from notifications.signals import notify
from notifications.utils import id2slug
from swapper import load_model

Notification = load_model('notifications', 'Notification')

try:
    # Django >= 1.7
    from django.test import override_settings  # noqa
except ImportError:
    # Django <= 1.6
    from django.test.utils import override_settings  # noqa

try:
    # Django >= 1.7
    from django.urls import reverse
except ImportError:
    # Django <= 1.6
    from django.core.urlresolvers import reverse  # pylint: disable=no-name-in-module,import-error




class NotificationTestPages(TestCase):
    ''' Django notifications automated page tests '''
    def setUp(self):
        self.message_count = 10
        self.from_user = User.objects.create_user(username="from", password="pwd", email="example@example.com")
        self.to_user = User.objects.create_user(username="to", password="pwd", email="example@example.com")
        self.to_user.is_staff = True
        self.to_user.save()
        for _ in range(self.message_count):
            notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)

    def logout(self):
        self.client.post(reverse('admin:logout')+'?next=/', {})

    def login(self, username, password):
        self.logout()
        response = self.client.post(reverse('login'), {'username': username, 'password': password})
        self.assertEqual(response.status_code, 302)
        return response

    def test_all_messages_page(self):
        self.login('to', 'pwd')
        response = self.client.get(reverse('notifications:all'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.all()))

    
    def test_next_pages(self):
        self.login('to', 'pwd')
        query_parameters = '?var1=hello&var2=world'

        response = self.client.get(reverse('notifications:mark_all_as_read'),data={
            "next": reverse('notifications:unread')  + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_read', args=[slug]), data={
            "next": reverse('notifications:unread') + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:mark_as_unread', args=[slug]), {
            "next": reverse('notifications:unread') + query_parameters,
        })
        self.assertRedirects(response, reverse('notifications:unread') + query_parameters)

    def test_delete_messages_pages(self):
        self.login('to', 'pwd')

        slug = id2slug(self.to_user.notifications.first().id)
        response = self.client.get(reverse('notifications:delete', args=[slug]))
        self.assertRedirects(response, reverse('notifications:all'))

        response = self.client.get(reverse('notifications:all'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['notifications']), len(self.to_user.notifications.all()))
        self.assertEqual(len(response.context['notifications']), self.message_count-1)


    

    def test_all_count_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_all_notification_count'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(list(data.keys()), ['all_count'])
        self.assertEqual(data['all_count'], self.message_count + 1)




    def test_all_list_api(self):
        self.login('to', 'pwd')

        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        response = self.client.get(reverse('notifications:live_all_notification_list'), data={"max": 5})
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), 5)

        # Test with a bad 'max' value
        response = self.client.get(reverse('notifications:live_all_notification_list'), data={
            "max": "this_is_wrong",
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        Notification.objects.filter(recipient=self.to_user).mark_all_as_read()
        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count)
        self.assertEqual(len(data['all_list']), self.message_count)

        notify.send(self.from_user, recipient=self.to_user, verb='commented', action_object=self.from_user)
        response = self.client.get(reverse('notifications:live_all_notification_list'))
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(list(data.keys())), ['all_count', 'all_list'])
        self.assertEqual(data['all_count'], self.message_count + 1)
        self.assertEqual(len(data['all_list']), self.message_count)
        self.assertEqual(data['all_list'][0]['verb'], 'commented')
        self.assertEqual(data['all_list'][0]['slug'], id2slug(data['all_list'][0]['id']))
