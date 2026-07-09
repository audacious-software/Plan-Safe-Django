# pylint: disable=line-too-long, super-with-arguments

from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.utils.safestring import mark_safe

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

from .models import Participant, TimeZone, StudyArm, SafetyPlan, SafetyPlanVersion, ReasonForLiving, CrisisHelpLine

class PrettyJSONWidgetFixed(PrettyJSONWidget):
    def render(self, name, value, attrs=None, **kwargs):
        return mark_safe(super(PrettyJSONWidgetFixed, self).render(name, value, attrs=None, **kwargs)) # nosec

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'fetch_phone_number', 'login_token', 'personalized_name', 'time_zone', 'created', 'updated',)
    list_filter = ('active', 'time_zone', 'created', 'updated',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidgetFixed(attrs={'initial': 'parsed'})}
    }

    def mark_inactive(self, request, queryset): # pylint: disable=unused-argument, no-self-use
        queryset.update(active=False)

    mark_inactive.short_description = "Mark selected participants inactive"

    def mark_active(self, request, queryset): # pylint: disable=unused-argument, no-self-use
        queryset.update(active=True)

    mark_active.short_description = "Mark selected participants active"

    actions = [mark_inactive, mark_active]

@admin.register(TimeZone)
class TimeZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'friendly_name', 'country_code',)
    list_filter = ('country_code',)

@admin.register(StudyArm)
class StudyArmAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier',)

@admin.register(SafetyPlan)
class SafetyPlanAdmin(admin.ModelAdmin):
    list_display = ('participant', 'created', 'last_updated')

@admin.register(SafetyPlanVersion)
class SafetyPlanVersionAdmin(admin.ModelAdmin):
    list_display = ('participant', 'safety_plan', 'version_created')
    list_filter = ('version_created', 'participant',)

    readonly_fields = (
        'safety_plan',
        'version_created',
        'participant',
        'created',
        'last_updated',
        'warning_signs',
        'coping_skills',
        'environmental_safety',
        'people_distraction',
        'message_distraction',
        'people_help',
        'message_help',
        'people_medical_provider',
        'message_medical_provider',
        'people_mental_health_provider',
        'message_mental_health_provider',
        'people_provider',
        'metadata',
        'crisis_help_lines',
    )

@admin.register(ReasonForLiving)
class ReasonForLivingAdmin(admin.ModelAdmin):
    list_display = ('safety_plan', 'created', 'caption')

@admin.register(CrisisHelpLine)
class CrisisHelpLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_label', 'voice_url', 'messaging_url', 'website',)
    search_fields = ('name', 'voice_url', 'messaging_url', 'voice_label', 'messaging_label', 'website',)
