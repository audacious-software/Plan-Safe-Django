# pylint: disable=no-member, line-too-long

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from simple_messaging.models import OutgoingMessage

from .models import Participant

def fetch_phone_number(identifier):
    matched = Participant.objects.filter(identifier=identifier).first()

    if matched is not None:
        return matched.fetch_phone_number()

    return None

def encrypt_addresses():
    for participant in Participant.objects.all():
        participant.set_phone_number(participant.fetch_phone_number())

def disable_keywords_for_message(incoming_message):
    sender = incoming_message.current_sender()

    now = timezone.now()

    participant_found = False

    for participant in Participant.objects.all():
        if sender == participant.current_phone_number():
            participant_found = True

            start_date = participant.translate_to_localtime(participant.created).date()

            today = participant.translate_to_localtime(now).date()

            day_index = (today - start_date).days - participant.days_paused() - participant.days_overlapped()

            if day_index >= settings.PLAN_SAFE_TOTAL_PROGRAM_DAYS:
                return True

    if participant_found:
        return False

    return True

def process_incoming_message(incoming_message):
    if disable_keywords_for_message(incoming_message):
        now = timezone.now()

        message = settings.PLAN_SAFE_UNMONITORED_MESSAGE

        outgoing = OutgoingMessage.objects.create(destination=incoming_message.current_sender(), send_date=now, message=message)
        outgoing.encrypt_destination()

        call_command('simple_messaging_send_pending_messages')
