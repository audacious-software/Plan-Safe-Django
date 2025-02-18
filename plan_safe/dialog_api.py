# pylint: disable=no-member, line-too-long, fixme

import json
import traceback
import urllib

from django_dialog_engine.dialog import BaseNode, DialogTransition
from django.template import engines

from .models import Participant, SafetyPlan, CrisisHelpLine

class UpdateSafetyPlanNode(BaseNode):
    @staticmethod
    def parse(dialog_def):
        if dialog_def['type'] == 'plan-safe-update-safety-plan':
            try:
                text_node = UpdateSafetyPlanNode(dialog_def['id'], dialog_def['next_id'], dialog_def.get('field', None), dialog_def.get('value', None), dialog_def.get('operation', None))

                return text_node
            except KeyError:
                traceback.print_exc()

        return None

    def __init__(self, node_id, next_node_id, field, value, operation):# pylint: disable=too-many-arguments
        super(UpdateSafetyPlanNode, self).__init__(node_id, node_id) # pylint: disable=super-with-arguments

        self.next_node_id = next_node_id
        self.field = field
        self.operation = operation

        if value is not None:
            value = value.replace('&', '\n')
            value = value.replace('\r', '\n')

            while '\n\n' in value:
                value = value.replace('\n\n', '\n')

            self.value = value.splitlines()
        else:
            self.value = []

    def node_type(self):
        return 'plan-safe-update-safety-plan'

    def str(self):
        definition = {
            'id': self.node_id,
            'next_id': self.next_node_id,
            'field': self.field,
            'value': self.value,
            'operation': self.operation,
        }

        return json.dumps(definition, indent=2)

    def evaluate(self, dialog, response=None, last_transition=None, extras=None, logger=None): # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument
        safety_plan = extras.get('plan_safe_safety_plan', None)

        django_engine = engines["django"]

        rendered_values = []

        for value in self.value:
            stripped_value = value.strip()

            if stripped_value.startswith('{{') and stripped_value.endswith('}}'):
                stripped_value = stripped_value[2:-2]

                if ('{{' in stripped_value) or ('}}' in stripped_value):
                    pass
                else:
                    variable_name = stripped_value.strip()

                    variable_value = extras.get(variable_name, None)

                    if variable_value is not None:
                        rendered_values.append(variable_value)

                        continue

            template = django_engine.from_string(value)

            rendered_value = template.render(extras)

            for line in rendered_value.splitlines():
                rendered_values.append(line)

        if self.field == 'coping-skills':
            if self.operation == 'operation-add':
                safety_plan.add_coping_skills(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_coping_skills(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_coping_skills()
        elif self.field == 'warning-signs':
            if self.operation == 'operation-add':
                safety_plan.add_warning_signs(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_warning_signs(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_warning_signs()
        elif self.field == 'environmental-safety':
            if self.operation == 'operation-add':
                safety_plan.add_environmental_safeties(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_environmental_safeties(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_environmental_safety()
        elif self.field == 'people-distraction':
            if self.operation == 'operation-add':
                safety_plan.add_people_distractions(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_people_distractions(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_people_distraction()
        elif self.field == 'people-help':
            if self.operation == 'operation-add':
                safety_plan.add_people_helps(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_people_helps(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_people_help()
        elif self.field == 'provider-medical':
            if self.operation == 'operation-add':
                safety_plan.add_people_medical_providers(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_people_medical_providers(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_people_medical_provider()
        elif self.field == 'provider-mental-health':
            if self.operation == 'operation-add':
                safety_plan.add_people_mental_health_providers(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_people_mental_health_providers(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_people_mental_health_provider()
        elif self.field == 'reasons-for-living':
            if self.operation == 'operation-add':
                safety_plan.add_reasons_for_living(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_reasons_for_living(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_reason_for_living()
        elif self.field == 'crisis-helplines':
            if self.operation == 'operation-add':
                safety_plan.add_crisis_help_lines(rendered_values)
            elif self.operation == 'operation-remove':
                safety_plan.remove_crisis_help_lines(rendered_values)
            elif self.operation == 'operation-reset':
                safety_plan.reset_crisis_help_line()

        transition = DialogTransition(new_state_id=self.next_node_id)

        transition.metadata['reason'] = 'updated-plan-safe-safety-plan'
        transition.metadata['exit_actions'] = []

        return transition

    def actions(self):
        return []

    def next_nodes(self):
        nodes = [
            (self.next_node_id, 'Next',),
        ]

        return nodes


def dialog_builder_cards():
    return [
        ('Plan Safe: Update Safety Plan', 'plan-safe-update-safety-plan',),
    ]


def identify_script_issues(script): # pylint: disable=unused-argument
    issues = []

    # TBD

    return issues

def fetch_destination_variables(destination):
    variables = {}

    for participant in Participant.objects.all():
        if participant.fetch_phone_number() == destination:
            variables['plan_safe_safety_plan_url'] = participant.get_absolute_url()

            safety_plan = participant.safety_plans.order_by('-created').first()

            if safety_plan is None:
                safety_plan = SafetyPlan.objects.create(participant=participant)

            variables['plan_safe_safety_plan'] = safety_plan

            variables['crisis_lines'] = CrisisHelpLine.objects.all().order_by('order_label')

    return variables

