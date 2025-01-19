from django import template

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
