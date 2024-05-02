# pylint: disable=no-member, line-too-long

import datetime
import json

import arrow
import humanize
import phonenumbers
import pytz

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django_dialog_engine.models import DialogScript, Dialog

from simple_messaging.models import IncomingMessage, OutgoingMessage
from simple_messaging_dialog_support.models import DialogSession

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

    query = DialogScript.objects.all().order_by('name')

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
def dashboard_schedule(request): # pylint: disable=too-many-locals
    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        identifier = request.POST.get('identifier', '')
        interrupt_minutes = int(request.POST.get('interrupt_minutes', ''))
        pause_minutes = int(request.POST.get('pause_minutes', ''))
        timeout_minutes = int(request.POST.get('timeout_minutes', ''))
        dialog_variables = request.POST.get('dialog_variables', '').split('\n')

        request.session['dialog_variables'] = '\n'.join(dialog_variables)

        phone = request.POST.get('phone', '')

        phones = phone.split(',')

        for phone_number in phones:
            phone_number = phone_number.strip()

            if phone_number != '':
                when = max(arrow.get(request.POST.get('date', '')).replace(tzinfo=pytz.timezone(settings.TIME_ZONE)).datetime, timezone.now())

                parsed = phonenumbers.parse(phone_number, settings.PHONE_REGION)

                destination = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

                script = DialogScript.objects.filter(identifier=identifier).first()

                if script is not None:
                    message = 'dialog:%s' % script.identifier

                    dialog_options = {
                        'interrupt_minutes': interrupt_minutes,
                        'pause_minutes': pause_minutes,
                        'timeout_minutes': timeout_minutes
                    }

                    for variable in dialog_variables:
                        pair = variable.split('=')

                        if len(pair) > 1:
                            dialog_options[pair[0].strip()] = pair[1].strip()

                    outgoing = OutgoingMessage.objects.create(destination=destination, send_date=when, message=message)
                    outgoing.message_metadata = json.dumps(dialog_options, indent=2)
                    outgoing.encrypt_destination()

        response_json = {
            'message': 'Dialog scheduled successfully.'
        }

        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json')

    return HttpResponseRedirect(reverse('dashboard_dialogs'))
