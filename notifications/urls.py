''' Django notification urls file '''
# -*- coding: utf-8 -*-
from distutils.version import StrictVersion  # pylint: disable=no-name-in-module,import-error

from django import get_version

from . import views

if StrictVersion(get_version()) >= StrictVersion('2.0'):
    from django.urls import re_path as pattern
else:
    from django.conf.urls import url as pattern


urlpatterns = [
    pattern(r'^$', views.AllNotificationsList.as_view(), name='all'),
    pattern(r'^delete/(?P<slug>\d+)/$', views.delete, name='delete'),
    pattern(r'^api/all_count/$', views.live_all_notification_count, name='live_all_notification_count'),
    pattern(r'^api/all_list/', views.live_all_notification_list, name='live_all_notification_list'),
]

app_name = 'notifications'
