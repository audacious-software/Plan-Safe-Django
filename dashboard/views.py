# pylint: disable=no-member, line-too-long

import datetime
import json
import random

import arrow
import humanize
import phonenumbers
import pytz

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.management import call_command
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import DialogScript, Dialog

from simple_messaging.models import IncomingMessage, OutgoingMessage, OutgoingMessageMedia
from simple_messaging_dialog_support.models import DialogSession

from plan_safe.models import Participant, TimeZone, StudyArm

@login_required
def dashboard_home(request):
    context = {}

    context['active_sessions'] = DialogSession.objects.filter(finished=None)
    context['completed_sessions'] = DialogSession.objects.exclude(finished=None)
    context['oldest_active_session'] = DialogSession.objects.filter(finished=None).order_by('started').first()

    cumulative_duration = 0
    completed_count = 0

    for session in context['completed_sessions']:
        cumulative_duration += (session.finished - session.started).total_seconds()
        completed_count += 1

    try:
        context['average_session_duration'] = cumulative_duration / completed_count
        context['average_session_duration_humanized'] = humanize.naturaldelta(datetime.timedelta(seconds=(cumulative_duration / completed_count))) # pylint: disable=superfluous-parens
    except ZeroDivisionError:
        context['average_session_duration_humanized'] = '(No data yet)'
        context['average_session_duration'] = -1

    context['incoming_messages'] = IncomingMessage.objects.all()
    context['outgoing_messages_sent'] = OutgoingMessage.objects.exclude(sent_date=None)
    context['outgoing_messages_pending'] = OutgoingMessage.objects.filter(sent_date=None)

    return render(request, 'dashboard_home.html', context=context)

@login_required
def dashboard_dialogs(request):
    context = {}

    query = DialogScript.objects.exclude(labels__icontains='archived').order_by('name')

    context['total'] = query.count()

    context['dialogs'] = query

    page = int(request.GET.get('page', '0'))
    page_size = int(request.GET.get('size', '25'))

    start_item = page_size * page

    if page_size != -1:
        context['dialogs'] = context['dialogs'][start_item:(start_item+page_size)]

    context['current_page'] = page
    context['pages'] = context['total'] // page_size
    context['size'] = page_size

    context['end_item'] = start_item + page_size

    if page_size == -1:
        context['current_page'] = 0
        context['pages'] = 1

        start_item = 0
        context['end_item'] = context['total']

    if context['end_item'] > context['total']:
        context['end_item'] = context['total']

    context['start_item'] = start_item + 1

    base_url = reverse('dashboard_dialogs')

    if page > 0:
        context['previous_page'] = '%s?page=%s&size=%s' % (base_url, page - 1, page_size,)

    if context['total'] > (page + 1) * page_size:
        context['next_page'] = '%s?page=%s&size=%s' % (base_url, page + 1, page_size,)

    context['first_page'] = '%s?page=%s&size=%s' % (base_url, 0, page_size,)

    context['last_page'] = '%s?page=%s&size=%s' % (base_url, context['pages'], page_size,)

    if page_size == -1:
        context['last_page'] = '%s?page=%s&size=%s' % (base_url, 0, page_size,)
        del context['next_page']

    if (context['total'] % page_size) != 0:
        context['pages'] += 1

    return render(request, 'dashboard_dialogs.html', context=context)

@login_required
def dashboard_logout(request):
    logout(request)

    return HttpResponseRedirect(reverse('dashboard_home'))

@login_required
def dashboard_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        identifier = request.POST.get('identifier', '')

        template_script = DialogScript.objects.filter(identifier=identifier).first()

        if template_script is None:
            template_script = DialogScript.objects.filter(identifier='default').first()

        if identifier == '':
            identifier = slugify(name)

        identifier_template = identifier
        identifier_index = 1

        while DialogScript.objects.filter(identifier=identifier).count() > 0:
            identifier = identifier_template + '-' + str(identifier_index)

            identifier_index += 1

        new_dialog = DialogScript.objects.create(name=name, identifier=identifier, definition=template_script.definition)

        response_json = {
            'name': new_dialog.name,
            'identifier': new_dialog.identifier,
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseBadRequest('Invalid Request', status=405)

@login_required
def dashboard_delete(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', None)

        response_json = {
            'deleted': DialogScript.objects.filter(identifier=identifier).delete()
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseBadRequest('Invalid Request', status=405)

@login_required
def dashboard_start(request):
    if request.method == 'POST':
        destination = request.POST.get('destination', '')
        identifier = request.POST.get('identifier', '')

        parsed = phonenumbers.parse(destination, settings.PHONE_REGION)

        destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

        script = DialogScript.objects.filter(identifier=identifier).first()

        if script is not None:
            new_dialog = Dialog.objects.create(key=script.identifier, script=script, dialog_snapshot=script.definition, started=timezone.now())

            existing_sessions = DialogSession.objects.filter(destination=destination, finished=None)

            for session in existing_sessions:
                session.finished = timezone.now()
                session.save()

                session.dialog.finish('user_cancelled')

            dialog_session = DialogSession.objects.create(destination=destination, dialog=new_dialog, started=timezone.now(), last_updated=timezone.now())

            response_json = {
                'session': dialog_session.pk
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseBadRequest('Invalid Request', status=405)

@login_required
def dashboard_schedule(request): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        identifier = request.POST.get('identifier', '')

        interrupt_minutes = None
        interrupt_str = request.POST.get('interrupt_minutes', '-1')

        try:
            interrupt_minutes = float(interrupt_str)
        except ValueError:
            pass

        pause_minutes = None
        pause_str = request.POST.get('pause_minutes', '-1')

        try:
            pause_minutes = float(pause_str)
        except ValueError:
            pass

        timeout_minutes = None
        timeout_str = request.POST.get('timeout_minutes', '-1')

        try:
            timeout_minutes = float(timeout_str)
        except ValueError:
            pass

        dialog_variables = request.POST.get('dialog_variables', '').split('\n')

        request.session['dialog_variables'] = '\n'.join(dialog_variables)

        phone = request.POST.get('phone', '')

        phones = phone.split(',')

        for phone_number in phones:
            phone_number = phone_number.strip()

            if phone_number != '':
                when = max(arrow.get(request.POST.get('date', '')).replace(tzinfo=pytz.timezone(settings.TIME_ZONE)).datetime, timezone.now())

                destination = None

                original_id = phone_number

                participant = Participant.objects.filter(identifier__iexact=phone_number).first()

                if participant is not None:
                    phone_number = participant.fetch_phone_number()

                try:
                    parsed = phonenumbers.parse(phone_number, settings.PHONE_REGION)

                    destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

                    script = DialogScript.objects.filter(identifier=identifier).first()

                    if script is not None:
                        message = 'dialog:%s' % script.identifier

                        dialog_options = {}

                        if interrupt_minutes is not None and interrupt_minutes < 0:
                            dialog_options['interrupt_minutes'] = interrupt_minutes

                        if timeout_minutes is not None and timeout_minutes < 0:
                            dialog_options['timeout_minutes'] = timeout_minutes

                        if pause_minutes is not None and pause_minutes < 0:
                            dialog_options['pause_minutes'] = pause_minutes

                        for variable in dialog_variables:
                            pair = variable.split('=')

                            if len(pair) > 1:
                                dialog_options[pair[0].strip()] = pair[1].strip()

                        outgoing = OutgoingMessage.objects.create(destination=destination, send_date=when, message=message)
                        outgoing.message_metadata = json.dumps(dialog_options, indent=2)
                        outgoing.encrypt_destination()
                except phonenumbers.phonenumberutil.NumberParseException:
                    response_json = {
                        'message': 'Unable to locate participant with identifier "%s". Please check and try again.' % original_id
                    }

                    return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')


        response_json = {
            'message': 'Dialog scheduled successfully.'
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseRedirect(reverse('dashboard_dialogs'))

@login_required
def dashboard_participants(request): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    context = {
    }

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '')
        phone_number = request.POST.get('phone_number', '')
        personalized_name = request.POST.get('personalized_name', '')
        time_zone = request.POST.get('time_zone', '')
        study_arm = request.POST.get('study_arm', '')

        if '' in [identifier, phone_number, personalized_name, time_zone, study_arm]:
            response_json = {
                'message': 'Please complete all the fields to proceed.',
                'reload': False
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

        try:
            parsed = phonenumbers.parse(phone_number, settings.PHONE_REGION)

            phone_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except: # pylint: disable=bare-except
            response_json = {
                'message': 'Phone number does not appear to be valid. Please re-enter and try again.',
                'reload': False
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

        participant = None

        for test_participant in Participant.objects.all():
            if test_participant.fetch_phone_number() == phone_number or test_participant.identifier == identifier:
                participant = test_participant

        if participant is None:
            participant = Participant.objects.create(identifier=identifier, phone_number=phone_number, time_zone=TimeZone.objects.get(name=time_zone), study_arm=StudyArm.objects.get(identifier=study_arm), personalized_name=personalized_name)

            response_json = {
                'message': 'Participant enrolled successfully.',
                'reload': True
            }
        else:
            response_json = {
                'message': 'Participant updated successfully.',
                'reload': True
            }

            participant.identifier = identifier
            participant.phone_number = phone_number
            participant.time_zone = TimeZone.objects.get(name=time_zone)
            participant.study_arm = StudyArm.objects.get(identifier=study_arm)
            participant.personalized_name = personalized_name

        participant.save()

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    search_query = request.GET.get('query', '')

    query = Participant.objects.all()

    study_arm = request.GET.get('study_arm', '')

    if study_arm != '':
        query = query.filter(study_arm__identifier=study_arm)

    context['participants'] = list(query.order_by('identifier'))
    context['selected_arm'] = study_arm

    context['search_query'] = search_query

    if search_query != '':
        new_participants = []

        for participant in context['participants']:
            metadata = json.dumps(participant.metadata)

            if search_query in metadata:
                new_participants.append(participant)
            elif search_query in str(participant.identifier):
                new_participants.append(participant)
            elif search_query in str(participant.phone_number):
                new_participants.append(participant)
            elif search_query in str(participant.personalized_name):
                new_participants.append(participant)

        context['participants'] = new_participants

    context['total'] = len(context['participants'])

    page = int(request.GET.get('page', '0'))
    page_size = int(request.GET.get('size', '25'))

    start_item = page_size * page

    if page_size != -1:
        context['participants'] = context['participants'][start_item:(start_item+page_size)]

    context['current_page'] = page
    context['pages'] = context['total'] / page_size
    context['size'] = page_size

    context['end_item'] = start_item + page_size

    if page_size == -1:
        context['current_page'] = 0
        context['pages'] = 1

        start_item = 0
        context['end_item'] = context['total']

    if context['end_item'] > context['total']:
        context['end_item'] = context['total']

    context['start_item'] = start_item + 1

    base_url = reverse('dashboard_participants')

    if page > 0:
        context['previous_page'] = '%s?page=%s&size=%s' % (base_url, page - 1, page_size)

    if context['total'] > (page + 1) * page_size:
        context['next_page'] = '%s?page=%s&size=%s' % (base_url, page + 1, page_size)

    context['first_page'] = '%s?page=%s&size=%s' % (base_url, 0, page_size)

    context['last_page'] = '%s?page=%s&size=%s' % (base_url, context['total'] / page_size, page_size)

    if page_size == -1:
        context['last_page'] = '%s?page=%s&size=%s' % (base_url, 0, page_size)
        del context['next_page']

    if (context['total'] % page_size) != 0:
        context['pages'] += 1

    context['time_zones'] = TimeZone.objects.all().order_by('order')
    context['study_arms'] = StudyArm.objects.all().order_by('name')

    return render(request, 'dashboard_participants.html', context=context)

@never_cache
@login_required
def dashboard_participants_broadcast(request): # pylint: disable=invalid-name
    if request.method == 'POST':
        identifiers = json.loads(request.POST.get('identifiers', '[]'))
        message = request.POST.get('message', None)
        when = request.POST.get('when', '')

        if message is not None and message.strip() != '':
            for identifier in identifiers:
                participant = Participant.objects.filter(identifier=identifier).first()

                when_send = timezone.now()

                if when != '':
                    when_send = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.strptime(when, '%Y-%m-%dT%H:%M'))

                if participant is not None:
                    outgoing = OutgoingMessage.objects.create(destination=participant.fetch_phone_number(), send_date=when_send, message=message)
                    outgoing.encrypt_destination()

                    outgoing_files = []

                    for key in request.FILES.keys():
                        outgoing_files.append(request.FILES[key])

                    index_counter = 0

                    for outgoing_file in outgoing_files:
                        media = OutgoingMessageMedia(message=outgoing)

                        media.content_type = outgoing_file.content_type
                        media.index = index_counter

                        media.save()

                        index_counter += 1

                        media.content_file.save(outgoing_file.name, outgoing_file)

            call_command('simple_messaging_send_pending_messages')

            response_json = {
                'message': 'Message broadcast scheduled.',
                'reset': True,
                'reload': False
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

        response_json = {
            'message': 'No message provided. None sent.',
            'reset': True,
            'reload': False
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseRedirect(reverse('dashboard_participants'))

def dashboard_new_identifier(request): # pylint: disable=unused-argument
    identifier = None

    while identifier is None:
        numeric = '%s' % random.randint(0, 99999999) # nosec

        while len(numeric) < 8:
            numeric = '0' + numeric

        identifier = '%s%s' % (settings.PLAN_SAFE_ID_PREFIX, numeric)

        if Participant.objects.filter(identifier=identifier).count() > 0:
            identifier = None

    return HttpResponse(json.dumps({'identifier': identifier}, indent=2), content_type='application/json')
