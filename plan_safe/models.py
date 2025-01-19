# pylint: disable=no-member, line-too-long

import phonenumbers
import pytz

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

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


class SafetyPlan(models.Model): # pylint: disable=too-many-public-methods
    participant = models.ForeignKey(Participant, null=True, blank=True, related_name='safety_plans', on_delete=models.SET_NULL)

    created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)

    warning_signs = models.TextField(max_length=1048576, null=True, blank=True,)
    coping_skills = models.TextField(max_length=1048576, null=True, blank=True,)
    environmental_safety = models.TextField(max_length=1048576, null=True, blank=True,)

    crisis_help_lines = models.ManyToManyField(CrisisHelpLine, related_name='safety_plans')

    people_distraction = models.TextField(max_length=1048576, null=True, blank=True,)
    people_help = models.TextField(max_length=1048576, null=True, blank=True,)
    people_medical_provider = models.TextField(max_length=1048576, null=True, blank=True,)
    people_mental_health_provider = models.TextField(max_length=1048576, null=True, blank=True,)
    people_provider = models.TextField(max_length=1048576, null=True, blank=True,)

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
            to_add.append(new_item.strip())

        for item in updated_list:
            for new_item in new_items:
                if isinstance(item, dict):
                    item_name = item.get('name', '')

                    if item_name.strip().lower() == new_item.lower():
                        to_add.remove(new_item)

                        break

                elif item.strip().lower() == new_item.lower():
                    to_add.remove(new_item)

                    break

        updated_list.extend(to_add)

        return updated_list

    def remove_from_list(self, updated_list, to_remove): # pylint: disable=no-self-use
        new_list = updated_list.copy()

        for remove_item in to_remove:
            for item in updated_list:
                if isinstance(item, dict):
                    item_name = item.get('name', '')

                    if item_name.strip().lower() == remove_item.lower():
                        while item in new_list:
                            new_list.remove(item)

                elif item.strip().lower() == remove_item.strip().lower():
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
        people = self.people_distraction.splitlines()

        new_people = []

        for list_person in people:
            tokens = list_person.split(';')

            if tokens[0].lower() == person.lower():
                if message.strip() == '':
                    new_people.append(tokens[0])
                else:
                    new_people.append('%s; %s' % (tokens[0], message))
            else:
                new_people.append(list_person)

        self.people_distraction = '\n'.join(new_people)
        self.save()

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
        people = self.people_help.splitlines()

        new_people = []

        for list_person in people:
            tokens = list_person.split(';')

            if tokens[0].lower() == person.lower():
                if message.strip() == '':
                    new_people.append(tokens[0])
                else:
                    new_people.append('%s; %s' % (tokens[0], message))
            else:
                new_people.append(list_person)

        self.people_help = '\n'.join(new_people)
        self.save()

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
        people = self.people_medical_provider.splitlines()

        new_people = []

        for list_person in people:
            tokens = list_person.split(';')

            if tokens[0].lower() == person.lower():
                if message.strip() == '':
                    new_people.append(tokens[0])
                else:
                    new_people.append('%s; %s' % (tokens[0], message))
            else:
                new_people.append(list_person)

        self.people_medical_provider = '\n'.join(new_people)
        self.save()

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
        people = self.people_mental_health_provider.splitlines()

        new_people = []

        for list_person in people:
            tokens = list_person.split(';')

            if tokens[0].lower() == person.lower():
                if message.strip() == '':
                    new_people.append(tokens[0])
                else:
                    new_people.append('%s; %s' % (tokens[0], message))
            else:
                new_people.append(list_person)

        self.people_mental_health_provider = '\n'.join(new_people)
        self.save()

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

    def fetch_reason_for_living(self):
        reasons = []

        for reason in self.reason_for_living.all():
            reasons.append(reason)

        return reasons

    def add_reasons_for_living(self, reasons_for_living):
        for reason in reasons_for_living:
            if self.reason_for_living.filter(caption__iequals=reason.strip().lower()).count() == 0:
                ReasonForLiving.objects.create(safety_plan=self, created=timezone.now(), caption=reason.strip())

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
        for help_line in crisis_help_lines:
            if self.crisis_help_lines.filter(name__iequals=help_line.strip().lower()).count() == 0:
                existing_line = CrisisHelpLine.objects.filter(name__iequals=help_line).first()

                if existing_line is not None:
                    self.crisis_help_lines.add(existing_line)

    def remove_crisis_help_lines(self, crisis_help_lines):
        for help_line in crisis_help_lines:
            existing_line = self.crisis_help_lines.filter(name__iequals=help_line.strip().lower()).first()

            if existing_line is not None:
                self.crisis_help_lines.remove(existing_line)

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
