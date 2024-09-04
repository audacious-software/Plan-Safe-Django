# pylint: disable=no-member, line-too-long

import phonenumbers
import pytz

from django.db import models
from django.utils import timezone

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
    voice_number = models.CharField(max_length=1024, null=True, blank=True)
    messaging_number = models.CharField(max_length=1024, null=True, blank=True)
    website = models.URLField(max_length=2048, null=True, blank=True)

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

class SafetyPlan(models.Model):
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
