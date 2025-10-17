# pylint: disable=line-too-long, wrong-import-position

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url # pylint: disable=no-name-in-module
else:
    from django.conf.urls import url

from .views import plan_safe_safety_plan, plan_safe_contact_card

urlpatterns = [
    url(r'^safety-plan/(?P<token>.+)$', plan_safe_safety_plan, name='plan_safe_safety_plan'),
    url(r'^contact/(?P<token>.+)/plan-safe.vcf$', plan_safe_contact_card, name='plan_safe_contact_card'),
]
