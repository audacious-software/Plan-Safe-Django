
from django.utils import timezone

from django_dialog_engine.models import DialogScript

from .models import Participant

def fetch_scheduled_events_wip():
    events = []

    now = timezone.now()

    for participant in Participant.objects.all():
        start_date = participant.translate_to_localtime(participant.created).date()

        today = participant.translate_to_localtime(now).date()

        day_index = (today - start_date).days

        event_key = '%s_day_%s' % (participant.identifier, day_index)

        seen_dialogs = participant.fetch_dialogs(seen=True)

        if day_index == 0:
            events.append({
                'event_key': event_key,
                'action': 'simple_messaging.send_message',
                'when': now.isoformat(),
                'context': {
                    'destination': participant.fetch_phone_number(),
                    'message': 'dialog:%s' % 'welcome_dialog',
                }
            })

        elif day_index <= 7:
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
                for label in seen_dialogs['labels']:
                    if tag in eligible_tags:
                        eligible_labels.remove(label)

                if today == seen_dialogs['when'].date():
                    continue # Dialog already scheduled, go to next participant...

                if len(eligible_tags) == 0:
                    continue # All dialogs have been sent

                next_dialog_label = eligible_labels[0]

                next_script = DialogScript.objects.fetch_by_label(next_dialog_label).first()

                if next_script is not None:
                    when = None # Schedule at start of user's messaging window - to be added

                    events.append({
                        'event_key': event_key,
                        'action': 'simple_messaging.send_message',
                        'when': when,
                        'context': {
                            'destination': participant.fetch_phone_number(),
                            'message': 'dialog:%s' % next_script.identifier,
                        }
                    })
                else:
                    pass # TODO: alert that dialog missing label isn't available
        else:
            pass

    return events
