# pylint: disable=line-too-long, no-member

import logging
import random

from django.conf import settings
from django.utils import timezone

from django_dialog_engine.models import DialogScript

from .models import Participant

def schedule_day_message(participant, events, day_index): # pylint: disable=too-many-locals, too-many-branches
    now = timezone.now()

    today = participant.translate_to_localtime(now).date()

    seen_dialogs = participant.fetch_dialogs(seen=True)

    event_key = '%s_day_%s' % (participant.identifier, day_index)

    if day_index <= 7:
        eligible_labels = [
            'week-1-1',
            'week-1-2',
            'week-1-3',
            'week-1-4',
            'week-1-5',
            'week-1-6',
            'week-1-7',
        ]

        for seen_dialog in seen_dialogs:
            for label in seen_dialog['labels']:
                if label in eligible_labels:
                    eligible_labels.remove(label)

            if today == seen_dialog['when'].date():
                return # Dialog already scheduled, go to next participant...

            if len(eligible_labels) == 0:
                return # All dialogs have been sent

            next_dialog_label = eligible_labels[0]

            next_script = DialogScript.objects.fetch_by_label(next_dialog_label).first()

            if next_script is not None:
                when = participant.fetch_today_start()

                events.append({
                    'event_key': event_key,
                    'action': 'simple_messaging.send_message',
                    'when': when.isoformat(),
                    'context': {
                        'destination': participant.fetch_phone_number(),
                        'message': 'dialog:%s' % next_script.identifier,
                    }
                })

                return

            logging.error('plan_safe.simple_scheduling_api: Dialog %s is not available for scheduling.', next_dialog_label)
    elif participant.is_paused():
        return
    elif day_index < 28:
        # If paused today, skip - add pause days to retain followup-other-followup-other pattern

        # Check to see if session still open the next day

        # Only nudge open sessions during user's time window.

        if (day_index % 2) == 1: # Follow-up days
            follow_ups = [
                'follow-up-warning-signs',
                'follow-up-coping-skills',
                'follow-up-people-distraction',
                'follow-up-people-help',
                'follow-up-crisis-resources',
                'follow-up-environmental-safety',
                'follow-up-reasons-for-living',
            ]

            last_sent = None

            for seen_dialog in seen_dialogs:
                if seen_dialog['identifier'] in follow_ups:
                    follow_ups.remove(seen_dialog['identifier'])

                if last_sent is None or last_sent < seen_dialog['when'].date():
                    last_sent = seen_dialog['when'].date()

            if today == last_sent:
                return # Dialog already scheduled, go to next participant...

            if len(follow_ups) > 0:
                when = participant.fetch_today_start()

                events.append({
                    'event_key': event_key,
                    'action': 'simple_messaging.send_message',
                    'when': when.isoformat(),
                    'context': {
                        'destination': participant.fetch_phone_number(),
                        'message': 'dialog:%s' % follow_ups[0],
                    }
                })
        else: # Other days
            other_dialogs = []

            for script in DialogScript.objects.all():
                labels_list = script.labels_list()

                if 'other' in labels_list and 'to-use' in labels_list:
                    other_dialogs.append(script.identifier)

            last_sent = None

            for seen_dialog in seen_dialogs:
                if seen_dialog['identifier'] in other_dialogs:
                    other_dialogs.remove(seen_dialog['identifier'])

                if last_sent is None or last_sent < seen_dialog['when'].date():
                    last_sent = seen_dialog['when'].date()

            if today == last_sent:
                return # Dialog already scheduled, go to next participant...

            random.shuffle(other_dialogs)

            if len(other_dialogs) > 0:
                when = participant.fetch_today_start()

                events.append({
                    'event_key': event_key,
                    'action': 'simple_messaging.send_message',
                    'when': when,
                    'context': {
                        'destination': participant.fetch_phone_number(),
                        'message': 'dialog:%s' % other_dialogs[0],
                    }
                })
    elif day_index == 28:
        when = participant.fetch_today_start()
        events.append({
            'event_key': event_key,
            'action': 'simple_messaging.send_message',
            'when': when,
            'context': {
                'destination': participant.fetch_phone_number(),
                'message': 'dialog:%s' % 'concluding-dialog',
            }
        })

def fetch_scheduled_events_control(): # pylint: disable=invalid-name
    events = []

    now = timezone.now()

    for participant in Participant.objects.filter(metadata__is_control=True, active=True):
        start_date = participant.translate_to_localtime(participant.created).date()

        today = participant.translate_to_localtime(now).date()

        day_index = (today - start_date).days - settings.PLAN_SAFE_CONTROL_DELAY_DAYS - participant.days_paused()

        event_key = '%s_day_%s' % (participant.identifier, day_index)

        if day_index == 0 - settings.PLAN_SAFE_CONTROL_DELAY_DAYS:
            events.append({
                'event_key': event_key,
                'action': 'simple_messaging.send_message',
                'when': now.isoformat(),
                'context': {
                    'destination': participant.fetch_phone_number(),
                    'message': 'dialog:%s' % 'welcome-dialog',
                }
            })
        elif day_index > 0:
            schedule_day_message(participant, events, day_index)

    return events

def fetch_scheduled_events_experiment(): # pylint: disable=invalid-name
    events = []

    now = timezone.now()

    for participant in Participant.objects.filter(metadata__is_control=False, active=True):
        start_date = participant.translate_to_localtime(participant.created).date()

        today = participant.translate_to_localtime(now).date()

        day_index = (today - start_date).days - participant.days_paused()

        event_key = '%s_day_%s' % (participant.identifier, day_index)

        if day_index == 0:
            events.append({
                'event_key': event_key,
                'action': 'simple_messaging.send_message',
                'when': now.isoformat(),
                'context': {
                    'destination': participant.fetch_phone_number(),
                    'message': 'dialog:%s' % 'welcome-dialog',
                }
            })
        elif day_index > 0:
            schedule_day_message(participant, events, day_index)

    return events

def fetch_scheduled_events():
    events = []

    events.extend(fetch_scheduled_events_control())
    events.extend(fetch_scheduled_events_experiment())

    return events
