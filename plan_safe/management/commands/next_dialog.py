# pylint: disable=no-member, line-too-long
# -*- coding: utf-8 -*-

import json

import six

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from ...models import Participant

class Command(BaseCommand):
    help = 'Prints the next dialog for the speciried user'

    def add_arguments(self, parser):
        parser.add_argument('identifier', type=str)

    def handle(self, *args, **options): # pylint: disable=too-many-branches
        participant = Participant.objects.get(identifier=options.get('identifier', None))

        six.print_('%s: %s' % (participant.identifier, json.dumps(participant.fetch_dialogs(seen=True), indent=2, cls=DjangoJSONEncoder)))
