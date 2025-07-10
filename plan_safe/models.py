# pylint: disable=no-member, line-too-long

import random

from urllib.parse import urlparse

try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict

import phonenumbers
import pytz
import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from simple_messaging.models import encrypt_value, decrypt_value

SUPPORTER_ROLES = (
    ('distraction', 'Distraction',),
    ('help', 'Help',),
    ('medical', 'Medical Provider',),
    ('mental-health', 'Mental Heath Provider',),
    ('provider', 'Provider',),
)

class TimeZone(models.Model):
    name = models.CharField(max_length=1048576, unique=True)
    country_code = models.CharField(max_length=1048576)
    friendly_name = models.CharField(max_length=1048576, unique=True, null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self): # pylint: disable=invalid-str-returned
        return self.name

class StudyArm(models.Model):
    name = models.CharField(max_length=1048576, unique=True)
    identifier = models.CharField(max_length=1048576)

    def __str__(self): # pylint: disable=invalid-str-returned
        return self.name

class CrisisHelpLine(models.Model):
    name = models.CharField(max_length=1024)
    voice_url = models.CharField(max_length=1024, null=True, blank=True)
    voice_label = models.CharField(max_length=1024, null=True, blank=True)
    messaging_url = models.CharField(max_length=1024, null=True, blank=True)
    messaging_label = models.CharField(max_length=1024, null=True, blank=True)
    website = models.URLField(max_length=2048, null=True, blank=True)

    order_label = models.IntegerField(default=0)

    blurb = models.TextField(null=True, blank=True)

    is_warmline = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

class Participant(models.Model):
    identifier = models.CharField(max_length=4096, null=True, blank=True)
    phone_number = models.CharField(max_length=4096, null=True, blank=True)
    personalized_name = models.CharField(max_length=4096, null=True, blank=True)

    time_zone = models.ForeignKey(TimeZone, null=True, blank=True, related_name='participants', on_delete=models.SET_NULL)

    study_arm = models.ForeignKey(StudyArm, null=True, blank=True, related_name='participants', on_delete=models.SET_NULL)

    active = models.BooleanField(default=True)

    metadata = models.JSONField(default=dict)

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)

    login_token = models.CharField(max_length=1024, null=True, blank=True)

    def obfuscated_phone_number(self):
        return self.fetch_phone_number(obfuscated=True)

    def fetch_phone_number(self, obfuscated=False):
        phone_number = self.phone_number

        if self.phone_number is not None and self.phone_number.startswith('secret:'):
            phone_number = decrypt_value(self.phone_number)

        if obfuscated:
            phone_number = 'XXX-XXX-%s' % phone_number[-4:]

        return phone_number

    def set_phone_number(self, phone_number):
        if self.time_zone is None:
            self.time_zone = TimeZone.objects.all().first()

        parsed_number = phonenumbers.parse(phone_number, self.time_zone.country_code)

        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        self.phone_number = encrypt_value(formatted_number)

        self.save()

    def __str__(self): # pylint: disable=invalid-str-returned
        if self.identifier is not None:
            return self.identifier

        return str(self.fetch_phone_number(obfuscated=True))

    def translate_to_localtime(self, original): # pylint: disable=no-self-use
        here_tz = pytz.timezone(self.time_zone.name)

        return original.astimezone(here_tz)

    def fetch_safety_plan(self):
        return self.safety_plans.order_by('-created').first()

    def get_absolute_url(self):
        if self.login_token is None or self.login_token == '':  # nosec
            self.login_token = get_random_string(length=32)
            self.save()

        return '%s%s' % (settings.SITE_URL, reverse('plan_safe_safety_plan', args=[self.login_token]))

class SafetyPlan(models.Model): # pylint: disable=too-many-public-methods, too-many-instance-attributes
    participant = models.ForeignKey(Participant, null=True, blank=True, related_name='safety_plans', on_delete=models.SET_NULL)

    created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)

    warning_signs = models.TextField(max_length=1048576, null=True, blank=True,)
    coping_skills = models.TextField(max_length=1048576, null=True, blank=True,)
    environmental_safety = models.TextField(max_length=1048576, null=True, blank=True,)

    crisis_help_lines = models.ManyToManyField(CrisisHelpLine, related_name='safety_plans')

    people_distraction = models.TextField(max_length=1048576, null=True, blank=True,)
    message_distraction = models.TextField(max_length=8192, null=True, blank=True,)

    people_help = models.TextField(max_length=1048576, null=True, blank=True,)
    message_help = models.TextField(max_length=8192, null=True, blank=True,)

    people_medical_provider = models.TextField(max_length=1048576, null=True, blank=True,)
    message_medical_provider = models.TextField(max_length=8192, null=True, blank=True,)

    people_mental_health_provider = models.TextField(max_length=1048576, null=True, blank=True,)
    message_mental_health_provider = models.TextField(max_length=8192, null=True, blank=True,)

    people_provider = models.TextField(max_length=1048576, null=True, blank=True,)

    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return 'Safety plan for %s' % self.participant

    def fetch_list(self, list_obj): # pylint: disable=no-self-use
        to_return = []

        if list_obj is None:
            return to_return

        lower_items = []

        for item in list_obj.splitlines():
            if len(item.strip()) > 0:
                if (item.strip().lower() in lower_items) is False:
                    to_return.append(item.strip())
                    lower_items.append(item.strip().lower())

        return to_return

    def add_to_list(self, updated_list, new_items): # pylint: disable=no-self-use
        to_add = []

        for new_item in new_items:
            to_add.append(str(new_item).strip())

        for item in updated_list:
            for new_item in new_items:
                if isinstance(item, UserDict):
                    item_name = item.get('value', '')

                    if str(item_name).strip().lower() == str(new_item).lower():
                        to_add.remove(str(new_item))

                        break

                elif str(item).strip().lower() == str(new_item).lower():
                    if new_item in to_add:
                        to_add.remove(new_item)

                    break

        updated_list.extend(to_add)

        return updated_list

    def remove_from_list(self, updated_list, to_remove): # pylint: disable=no-self-use
        new_list = updated_list.copy()

        for remove_item in to_remove:
            for item in updated_list:
                if isinstance(item, UserDict):
                    item_name = item.get('value', '')

                    if str(item_name).strip().lower() == str(remove_item).lower():
                        while item in new_list:
                            new_list.remove(str(item))

                elif str(item).strip().lower() == str(remove_item).strip().lower():
                    while item in new_list:
                        new_list.remove(item)

        return new_list

    def fetch_coping_skills(self):
        return self.fetch_list(self.coping_skills)

    def add_coping_skills(self, coping_skills):
        updated_list = self.add_to_list(self.fetch_coping_skills(), coping_skills)

        self.coping_skills = '\n'.join(updated_list)
        self.save()

    def remove_coping_skills(self, coping_skills):
        updated_list = self.remove_from_list(self.fetch_coping_skills(), coping_skills)

        self.coping_skills = '\n'.join(updated_list)
        self.save()

    def reset_coping_skills(self):
        self.coping_skills = None
        self.save()

    def fetch_warning_signs(self):
        return self.fetch_list(self.warning_signs)

    def add_warning_signs(self, warning_signs):
        updated_list = self.add_to_list(self.fetch_warning_signs(), warning_signs)

        self.warning_signs = '\n'.join(updated_list)
        self.save()

    def remove_warning_signs(self, warning_signs):
        updated_list = self.remove_from_list(self.fetch_warning_signs(), warning_signs)

        self.warning_signs = '\n'.join(updated_list)
        self.save()

    def reset_warning_signs(self):
        self.warning_signs = None
        self.save()

    def fetch_people_distraction(self):
        people = self.fetch_list(self.people_distraction)

        people_list = []

        for person_str in people:
            tokens = person_str.split(';')

            person = {
                'name': tokens[0].strip()
            }

            if len(tokens) > 1:
                person['message'] = tokens[1].strip()

            people_list.append(person)

        return people_list

    def add_people_distractions(self, people_distractions):
        updated_list = self.add_to_list(self.fetch_people_distraction(), people_distractions)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_distraction = '\n'.join(new_list)
        self.save()

    def remove_people_distractions(self, people_distractions):
        updated_list = self.remove_from_list(self.fetch_people_distraction(), people_distractions)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_distraction = '\n'.join(new_list)
        self.save()

    def reset_people_distractions(self):
        self.people_distraction = None
        self.save()

    def update_people_distraction_message(self, person, message): # pylint: disable=invalid-name
        person = person.strip()
        message = message.strip()

        if person in ('', None):
            self.message_distraction = message
        else:
            people = []

            if self.people_distraction is not None and self.people_distraction.strip() != '':
                people = self.people_distraction.splitlines()

            new_people = []

            updated = False

            for list_person in people:
                tokens = list_person.split(';')

                if tokens[0].lower() == person.lower():
                    if message == '':
                        new_people.append(tokens[0])
                    else:
                        new_people.append('%s; %s' % (tokens[0], message))

                    updated = True
                else:
                    new_people.append(list_person)

            if updated is False:
                if message == '':
                    new_people.append(person)
                else:
                    new_people.append('%s; %s' % (person, message))

            self.people_distraction = '\n'.join(new_people)

        self.save()

    def fetch_default_people_distraction_message(self): # pylint: disable=invalid-name
        return self.message_distraction

    def fetch_people_help(self):
        people = self.fetch_list(self.people_help)

        people_list = []

        for person_str in people:
            tokens = person_str.split(';')

            person = {
                'name': tokens[0].strip()
            }

            if len(tokens) > 1:
                person['message'] = tokens[1].strip()

            people_list.append(person)

        return people_list

    def add_people_helps(self, people_helps):
        updated_list = self.add_to_list(self.fetch_people_help(), people_helps)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_help = '\n'.join(new_list)
        self.save()

    def remove_people_helps(self, people_helps):
        updated_list = self.remove_from_list(self.fetch_people_help(), people_helps)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_help = '\n'.join(new_list)
        self.save()

    def reset_people_help(self):
        self.people_help = None
        self.save()

    def update_people_help_message(self, person, message):
        person = person.strip()
        message = message.strip()

        if person in ('', None):
            self.message_help = message
        else:
            people = []

            if self.people_help is not None and self.people_help.strip() != '':
                people = self.people_help.splitlines()

            new_people = []

            updated = False

            for list_person in people:
                tokens = list_person.split(';')

                if tokens[0].lower() == person.lower():
                    if message == '':
                        new_people.append(tokens[0])
                    else:
                        new_people.append('%s; %s' % (tokens[0], message))

                    updated = True
                else:
                    new_people.append(list_person)

            if updated is False:
                if message == '':
                    new_people.append(person)
                else:
                    new_people.append('%s; %s' % (person, message))

            self.people_help = '\n'.join(new_people)

        self.save()

    def fetch_default_people_help_message(self): # pylint: disable=invalid-name
        return self.message_help

    def fetch_people_medical_provider(self):
        people = self.fetch_list(self.people_medical_provider)

        people_list = []

        for person_str in people:
            tokens = person_str.split(';')

            person = {
                'name': tokens[0].strip()
            }

            if len(tokens) > 1:
                person['message'] = tokens[1].strip()

            people_list.append(person)

        return people_list

    def add_people_medical_providers(self, people_medical_providers):
        updated_list = self.add_to_list(self.fetch_people_medical_provider(), people_medical_providers)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_medical_provider = '\n'.join(new_list)
        self.save()

    def remove_people_medical_providers(self, people_medical_providers):
        updated_list = self.remove_from_list(self.fetch_people_medical_provider(), people_medical_providers)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_medical_provider = '\n'.join(new_list)
        self.save()

    def reset_people_medical_provider(self):
        self.people_medical_provider = None
        self.save()

    def update_people_medical_message(self, person, message):
        person = person.strip()
        message = message.strip()

        if person in ('', None):
            self.message_medical_provider = message
        else:
            people = []

            if self.people_medical_provider is not None and self.people_medical_provider.strip() != '':
                people = self.people_medical_provider.splitlines()

            new_people = []

            updated = False

            for list_person in people:
                tokens = list_person.split(';')

                if tokens[0].lower() == person.lower():
                    if message == '':
                        new_people.append(tokens[0])
                    else:
                        new_people.append('%s; %s' % (tokens[0], message))

                    updated = True
                else:
                    new_people.append(list_person)

            if updated is False:
                if message == '':
                    new_people.append(person)
                else:
                    new_people.append('%s; %s' % (person, message))

            self.people_medical_provider = '\n'.join(new_people)

        self.save()

    def fetch_default_people_medical_message(self): # pylint: disable=invalid-name
        return self.message_medical_provider

    def fetch_people_mental_health_provider(self): # pylint: disable=invalid-name
        people = self.fetch_list(self.people_mental_health_provider)

        people_list = []

        for person_str in people:
            tokens = person_str.split(';')

            person = {
                'name': tokens[0].strip()
            }

            if len(tokens) > 1:
                person['message'] = tokens[1].strip()

            people_list.append(person)

        return people_list

    def add_people_mental_health_providers(self, people_mental_health_providers): # pylint: disable=invalid-name
        updated_list = self.add_to_list(self.fetch_people_mental_health_provider(), people_mental_health_providers)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_mental_health_provider = '\n'.join(new_list)
        self.save()

    def remove_people_mental_health_providers(self, people_mental_health_providers): # pylint: disable=invalid-name
        updated_list = self.remove_from_list(self.fetch_people_mental_health_provider(), people_mental_health_providers)

        new_list = []

        for item in updated_list:
            if isinstance(item, str):
                new_list.append(item)
            else:
                name = item.get('name', None)
                message = item.get('message', None)

                if message is not None:
                    new_list.append('%s; %s' % (name, message))
                else:
                    new_list.append(name)

        self.people_mental_health_provider = '\n'.join(new_list)
        self.save()

    def reset_people_mental_health_provider(self): # pylint: disable=invalid-name
        self.people_mental_health_provider = None
        self.save()

    def update_people_mental_health_message(self, person, message): # pylint: disable=invalid-name
        person = person.strip()
        message = message.strip()

        if person in ('', None):
            self.message_mental_health_provider = message
        else:
            people = []

            if self.people_mental_health_provider is not None and self.people_mental_health_provider.strip() != '':
                people = self.people_mental_health_provider.splitlines()

            new_people = []

            updated = False

            for list_person in people:
                tokens = list_person.split(';')

                if tokens[0].lower() == person.lower():
                    if message == '':
                        new_people.append(tokens[0])
                    else:
                        new_people.append('%s; %s' % (tokens[0], message))

                    updated = True
                else:
                    new_people.append(list_person)

            if updated is False:
                if message == '':
                    new_people.append(person)
                else:
                    new_people.append('%s; %s' % (person, message))

            self.people_mental_health_provider = '\n'.join(new_people)

        self.save()

    def add_helper_message(self, helper_type, helper_name, helper_message):
        if helper_name is not None:
            helper_name = ''.join(helper_name.splitlines())

        if helper_message is not None:
            helper_message = ''.join(helper_message.splitlines())

        if helper_type == 'distraction':
            self.update_people_distraction_message(helper_name, helper_message)
        elif helper_type == 'help':
            self.update_people_help_message(helper_name, helper_message)
        elif helper_type == 'medical':
            self.update_people_medical_message(helper_name, helper_message)
        elif helper_type == 'mental':
            self.update_people_mental_health_message(helper_name, helper_message)

    def fetch_default_people_mental_health_message(self): # pylint: disable=invalid-name
        return self.message_mental_health_provider

    def fetch_environmental_safety(self):
        return self.fetch_list(self.environmental_safety)

    def add_environmental_safeties(self, environmental_safeties):
        updated_list = self.add_to_list(self.fetch_environmental_safety(), environmental_safeties)

        self.environmental_safety = '\n'.join(updated_list)
        self.save()

    def remove_environmental_safeties(self, environmental_safeties):
        updated_list = self.remove_from_list(self.fetch_environmental_safety(), environmental_safeties)

        self.environmental_safety = '\n'.join(updated_list)
        self.save()

    def reset_environmental_safety(self):
        self.environmental_safety = None
        self.save()

    def fetch_reason_for_living(self, sample_count=None, avoid_repeats=False, sequential=False): # pylint: disable=too-many-branches
        seen_reasons = self.metadata.get('seen_reasons_for_living', [])

        reasons = []
        unseen = []

        for reason in self.reason_for_living.all().order_by('created'):
            reasons.append(reason)

            if (reason.pk in seen_reasons) is False:
                unseen.append(reason)

        if sample_count is None:
            sample_count = len(reasons)

        if len(unseen) == 0:
            unseen = reasons

        seen = [item for item in reasons if item not in unseen]

        if avoid_repeats:
            if len(reasons) >= sample_count:
                if sequential is False:
                    sampled = random.sample(seen, k=(sample_count - len(unseen)))
                else:
                    sampled = seen[:(sample_count - len(unseen))]

                unseen.extend(sampled)
            else:
                unseen = reasons
        elif sequential is False:
            unseen = random.sample(reasons, k=sample_count)

        if sequential is False:
            random.shuffle(unseen)

        for reason in unseen:
            seen_reasons.append(reason.pk)

        if len(seen_reasons) >= len(reasons):
            seen_reasons = []

        self.metadata['seen_reasons_for_living'] = seen_reasons # pylint: disable=unsupported-assignment-operation
        self.save()

        return unseen

    def add_reasons_for_living(self, reasons_for_living):
        for reason in reasons_for_living: # pylint: disable=too-many-nested-blocks
            reason_text = str(reason).strip()

            if reason_text == '' or self.reason_for_living.filter(caption__iexact=reason_text.lower()).count() == 0:
                reason_obj = ReasonForLiving.objects.create(safety_plan=self, created=timezone.now(), caption=reason_text.strip())

                if isinstance(reason, UserDict):
                    for media_item in reason.get('media', []):
                        media_type = media_item.get('type', '')

                        if media_type.startswith('image/'):
                            image_url = media_item.get('url', None)

                            if image_url is not None:
                                image_response = requests.get(image_url, timeout=300)

                                parsed = urlparse(image_url)

                                filename = parsed.path.split('/')[-1]

                                reason_obj.image.save(filename, ContentFile(image_response.content))

                                reason_obj.save()

                                break

    def add_reasons_for_living_from_url(self, caption=None, media_url=None):
        if caption is None:
            caption = ''

        reason_text = str(caption).strip()

        if caption == '' and media_url is not None:
            reason_obj = ReasonForLiving.objects.create(safety_plan=self, created=timezone.now(), caption=caption)
        else:
            reason_obj = self.reason_for_living.filter(caption__iexact=reason_text).first()

        if reason_obj is None:
            reason_obj = ReasonForLiving.objects.create(safety_plan=self, created=timezone.now(), caption=reason_text)

        if (media_url in (None, '')) is False:
            media_response = requests.get(media_url, timeout=300)

            media_type = media_response.headers.get('Content-Type', 'application/octet-stream')

            if media_type.startswith('image/'):
                parsed = urlparse(media_url)

                filename = parsed.path.split('/')[-1]

                reason_obj.image.save(filename, ContentFile(media_response.content))

                reason_obj.save()

    def remove_reasons_for_living(self, reasons_for_living):
        for reason in reasons_for_living:
            self.reason_for_living.filter(caption__iequals=reason.strip().lower()).delete()

    def reset_reason_for_living(self):
        self.reason_for_living.all().delete()

    def fetch_crisis_help_lines(self):
        help_lines = []

        for help_line in self.crisis_help_lines.all():
            help_lines.append(help_line)

        return help_lines

    def add_crisis_help_lines(self, crisis_help_lines):
        line_labels = []

        for help_line in crisis_help_lines:
            tokens = str(help_line).split()

            for token in tokens:
                if (token in line_labels) is False:
                    line_labels.append(token)

            for line_label in line_labels:
                try:
                    existing_line = CrisisHelpLine.objects.filter(order_label=int(line_label)).first()

                    if existing_line is not None:
                        self.crisis_help_lines.add(existing_line)
                except ValueError:
                    pass # Not found

        self.save()

    def remove_crisis_help_lines(self, crisis_help_lines):
        line_labels = []

        for help_line in crisis_help_lines:
            tokens = help_line.split()

            for token in tokens:
                if (token in line_labels) is False:
                    line_labels.append(token)

            for line_label in line_labels:
                try:
                    existing_line = CrisisHelpLine.objects.filter(order_label=int(line_label)).first()

                    if existing_line is not None:
                        self.crisis_help_lines.remove(existing_line)
                except ValueError:
                    pass # Not found

        self.save()

    def reset_crisis_help_line(self):
        self.crisis_help_lines.clear()

@receiver(pre_save, sender=SafetyPlan)
def pre_save_user(sender, instance, **kwargs): # pylint: disable=unused-argument
    instance.last_updated = timezone.now()

class Supporter(models.Model):
    safety_plan = models.ForeignKey(SafetyPlan, related_name='supporters', null=True, blank=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(default=timezone.now)

    name = models.CharField(max_length=2048, null=True, blank=True)
    contact = models.CharField(max_length=2048, null=True, blank=True)
    role = models.CharField(max_length=2048, choices=SUPPORTER_ROLES)
    message = models.TextField(max_length=1048576, null=True, blank=True)

class ReasonForLiving(models.Model):
    safety_plan = models.ForeignKey(SafetyPlan, related_name='reason_for_living', null=True, blank=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(default=timezone.now)

    caption = models.TextField(max_length=1048576, null=True, blank=True,)
    image = models.ImageField(upload_to='plan_safe/reasons_images', null=True, blank=True)

    def __str__(self):
        return str(self.caption)
