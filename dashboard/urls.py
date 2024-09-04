# pylint: disable=line-too-long, wrong-import-position

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url
else:
    from django.conf.urls import url

from .views import dashboard_home, dashboard_dialogs, dashboard_logout, dashboard_create, \
                   dashboard_delete, dashboard_start, dashboard_schedule, dashboard_participants, \
                   dashboard_participants_broadcast

urlpatterns = [
    url(r'^participants$', dashboard_participants, name='dashboard_participants'),
    url(r'^participants/broadcast$', dashboard_participants_broadcast, name='dashboard_participants_broadcast'),
    url(r'^delete$', dashboard_delete, name='dashboard_delete'),
    url(r'^create$', dashboard_create, name='dashboard_create'),
    url(r'^start$', dashboard_start, name='dashboard_start'),
    url(r'^schedule$', dashboard_schedule, name='dashboard_schedule'),
    url(r'^dialogs$', dashboard_dialogs, name='dashboard_dialogs'),
    url(r'^logout$', dashboard_logout, name='dashboard_logout'),
    url(r'^$', dashboard_home, name='dashboard_home'),
]
