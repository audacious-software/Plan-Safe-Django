# pylint: disable=line-too-long

from prettyjson import PrettyJSONWidget

from django.contrib import admin

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

from .models import Participant, TimeZone, StudyArm, SafetyPlan, ReasonForLiving, CrisisHelpLine

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'fetch_phone_number', 'login_token', 'personalized_name', 'time_zone', 'created', 'updated',)
    list_filter = ('active', 'time_zone', 'created', 'updated',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
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

@admin.register(ReasonForLiving)
class ReasonForLivingAdmin(admin.ModelAdmin):
    list_display = ('safety_plan', 'created', 'caption')

@admin.register(CrisisHelpLine)
class CrisisHelpLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_label', 'voice_url', 'messaging_url', 'website',)
    search_fields = ('name', 'voice_url', 'messaging_url', 'voice_label', 'messaging_label', 'website',)
