# pylint: disable=line-too-long, no-member

import json
import time

import phonenumbers

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .models import Participant, CrisisHelpLine, ReasonForLiving

def plan_safe_safety_plan(request, token): # pylint: disable=unused-argument, too-many-branches, too-many-locals, too-many-return-statements, too-many-statements
    if token.endswith('.'):
        return redirect('plan_safe_safety_plan', token=token[:-1])

    context = {
        'project_name': settings.SIMPLE_DATA_EXPORTER_SITE_NAME,
        'token': token,
    }

    token_user = Participant.objects.exclude(login_token=None).exclude(login_token='').filter(login_token=token).first() # nosec

    if token_user is None:
        raise Http404

    now_timestamp = int(time.time())

    last_access = request.session.get('plan_safe_last_profile_access', 0)

    if request.GET.get('expire', 'false') == 'true':
        last_access = 0

    needs_login = False

    if now_timestamp - last_access > settings.PLAN_SAFE_EXPIRE_SECONDS:
        needs_login = True

    if request.method == 'POST' and request.POST.get('auth_phone_number', None) is not None:
        parsed_number = phonenumbers.parse(request.POST.get('auth_phone_number', None), token_user.time_zone.country_code)

        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        if formatted_number != token_user.fetch_phone_number(): # pylint: disable=simplifiable-if-statement
            needs_login = True
        else:
            context['user'] = token_user

            needs_login = False

            request.session['plan_safe_last_profile_access'] = now_timestamp

            return redirect('plan_safe_safety_plan', token=token)

    if needs_login:
        return render(request, 'plan_safe_profile_auth.html', context=context)

    request.session['plan_safe_last_profile_access'] = now_timestamp

    safety_plan = token_user.fetch_safety_plan()

    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        action = request.POST.get('action',  None)
        section = request.POST.get('section',  None)
        value = request.POST.get('value',  '')

        if action is not None and section is not None:
            if value is not None:
                value = value.replace('&', '\n')
                value = value.replace('\r', '\n')

                values = []

                for value in value.splitlines():
                    values.append(value.strip())

                if action == 'add':
                    if section == 'warning_sign':
                        safety_plan.add_warning_signs(values)

                        response_json = {
                            'message': 'Success. %s added to warning signs.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'coping_skill':
                        safety_plan.add_coping_skills(values)

                        response_json = {
                            'message': 'Success. %s added to warning signs.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'environmental_safety':
                        safety_plan.add_environmental_safeties(values)

                        response_json = {
                            'message': 'Success. %s added to environmental safety.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_distraction':
                        safety_plan.add_people_distractions(values)

                        response_json = {
                            'message': 'Success. %s added to people for distraction.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_help':
                        safety_plan.add_people_helps(values)

                        response_json = {
                            'message': 'Success. %s added to people for help.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_medical':
                        safety_plan.add_people_medical_providers(values)

                        response_json = {
                            'message': 'Success. %s added to medical providers.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_mental':
                        safety_plan.add_people_mental_health_providers(values)

                        response_json = {
                            'message': 'Success. %s added to mental health providers.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                elif action == 'remove':
                    if section == 'warning_sign':
                        safety_plan.remove_warning_signs(values)

                        response_json = {
                            'message': 'Success. %s removed from warning signs.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'coping_skill':
                        safety_plan.remove_coping_skills(values)

                        response_json = {
                            'message': 'Success. %s removed from coping skills.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'environmental_safety':
                        safety_plan.remove_environmental_safeties(values)

                        response_json = {
                            'message': 'Success. %s removed from environmental safety.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_distraction':
                        safety_plan.remove_people_distractions(values)

                        response_json = {
                            'message': 'Success. %s removed from people for distraction.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_help':
                        safety_plan.remove_people_helps(values)

                        response_json = {
                            'message': 'Success. %s removed from people for help.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_medical':
                        safety_plan.remove_people_medical_providers(values)

                        response_json = {
                            'message': 'Success. %s removed from medical providers.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_mental':
                        safety_plan.remove_people_mental_health_providers(values)

                        response_json = {
                            'message': 'Success. %s removed from mental health providers.' % values
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                elif action == 'update-message':
                    person = request.POST.get('person',  None)

                    if section == 'person_distraction':
                        safety_plan.update_people_distraction_message(person, value)

                        response_json = {
                            'message': 'Success. Message updated.'
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_help':
                        safety_plan.update_people_help_message(person, value)

                        response_json = {
                            'message': 'Success. Message updated.'
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_medical':
                        safety_plan.update_people_medical_message(person, value)

                        response_json = {
                            'message': 'Success. Message updated.'
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                    if section == 'person_mental':
                        safety_plan.update_people_mental_health_message(person, value)

                        response_json = {
                            'message': 'Success. Message updated.'
                        }

                        return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)

                elif action == 'select-crisis-line':
                    line_pk = int(request.POST.get('line',  '-1'))
                    selected = request.POST.get('checked',  'false') == 'true'

                    help_line = CrisisHelpLine.objects.filter(pk=line_pk).first()

                    if help_line is not None:
                        if selected:
                            safety_plan.crisis_help_lines.add(help_line)
                        else:
                            safety_plan.crisis_help_lines.remove(help_line)

                    response_json = {
                        'message': 'Success. Line selection updated.'
                    }

                    return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=204)
                elif action == 'add-reason':
                    value = request.POST.get('value',  '')

                    reason = ReasonForLiving.objects.create(safety_plan=safety_plan, caption=value)

                    try:
                        reason.image = request.FILES['reason_file']
                        reason.save()
                    except KeyError:
                        pass

                    response_json = {
                        'message': 'Success. New reason for living created.',
                        'pk': reason.pk
                    }

                    if reason.image:
                        response_json['image'] = reason.image.url

                    return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=201)
                elif action == 'remove-reason':
                    item_pk = int(request.POST.get('value',  '-1'))

                    ReasonForLiving.objects.filter(pk=item_pk, safety_plan=safety_plan).delete()

                    response_json = {
                        'message': 'Success. Reason for living removed.'
                    }

                    return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=201)
        else:
            response_json = {
                'error': 'Invalid request. action = %s; section = %s' % (action, section)
            }

            return HttpResponse(json.dumps(response_json, indent=2), content_type='application/json', status=500)

    context['user'] = token_user
    context['crisis_help_lines'] = CrisisHelpLine.objects.all()

    selected_lines = []


    if safety_plan is not None:
        for line in safety_plan.crisis_help_lines.all():
            selected_lines.append(line.pk)

    context['selected_help_lines'] = selected_lines

    context['project_name'] = settings.SIMPLE_DATA_EXPORTER_SITE_NAME

    return render(request, 'plan_safe_safety_plan.html', context=context)
