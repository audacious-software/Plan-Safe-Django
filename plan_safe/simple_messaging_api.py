from .models import Participant

def fetch_phone_number(identifier):
    matched = Participant.objects.filter(identifier=identifier).first()

    if matched is not None:
        return matched.fetch_phone_number()

    return None
