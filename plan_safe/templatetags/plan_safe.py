# pylint: disable=line-too-long, too-many-arguments

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def parse_person(value):
    tokens = value.split(';')

    person = {
        'name': tokens[0]
    }

    if len(tokens) > 1:
        person['message'] = tokens[1]

    return person

@register.simple_tag
def show_people_message_list(safety_plan, message_type='distraction', intro='', counter_prefix='', counter_suffix='', include_global=True, global_prefix=None, empty_message=''):
    if global_prefix is None:
        global_prefix = 'A message you can send to any of them:'

    people = safety_plan.fetch_people_distraction()
    default_message = safety_plan.fetch_default_people_distraction_message()

    if message_type == 'help':
        people = safety_plan.fetch_people_help()
        default_message = safety_plan.fetch_default_people_help_message()
    elif  message_type == 'medical':
        people = safety_plan.fetch_people_medical_provider()
        default_message = safety_plan.fetch_default_people_medical_message()
    elif  message_type == 'mental_health':
        people = safety_plan.fetch_people_mental_health_provider()
        default_message = safety_plan.fetch_default_people_mental_health_message()

    if len(people) == 0:
        return empty_message

    rendered = ''

    if intro != '':
        rendered = '%s\n' % intro

    person_index = 1

    for person in people:
        rendered = '%s%s%s%s %s' % (rendered, counter_prefix, person_index, counter_suffix, person.get('name', ''))

        message = person.get('message', None)

        if message is not None:
            rendered = '%s - "%s"\n' % (rendered, message)
        else:
            rendered = '%s\n' % rendered

        person_index += 1

    if include_global and default_message is not None and default_message != '':
        rendered = '%s\n%s "%s"' % (rendered, global_prefix, default_message)

    rendered = rendered.strip()

    return mark_safe(rendered) # nosec
