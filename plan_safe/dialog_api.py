# pylint: disable=no-member, line-too-long, fixme

import datetime
import json
import logging
import traceback

from django.conf import settings
from django.template import engines
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from django_dialog_engine.dialog import BaseNode, DialogTransition, DialogMachine

from django_dialog_engine.models import DialogScript, apply_template

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

    def node_definition(self):
        node_def = super().node_definition() # pylint: disable=missing-super-argument

        node_def['field'] = self.field
        node_def['operation'] = self.operation
        node_def['value'] = '\n'.join(self.value)

        return node_def

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

        rendered_values = []

        for value in self.value:
            rendered_value = apply_template(value, extras)

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


class FetchReasonsForLivingNode(BaseNode):
    @staticmethod
    def parse(dialog_def):
        if dialog_def['type'] == 'plan-safe-fetch-reasons-for-living':
            try:
                fetch_node = FetchReasonsForLivingNode(dialog_def['id'], dialog_def['next_id'], dialog_def.get('empty_id', None), dialog_def.get('variable', None), dialog_def.get('count', 1), dialog_def.get('avoid_repeats', False))

                return fetch_node
            except KeyError:
                traceback.print_exc()

        return None

    def __init__(self, node_id, next_node_id, empty_node_id, variable, sample_count, avoid_repeats):# pylint: disable=too-many-arguments
        super(FetchReasonsForLivingNode, self).__init__(node_id, node_id) # pylint: disable=super-with-arguments

        self.next_node_id = next_node_id
        self.empty_node_id = empty_node_id
        self.variable = variable
        self.sample_count = sample_count
        self.avoid_repeats = avoid_repeats

    def node_type(self):
        return 'plan-safe-fetch-reasons-for-living'

    def str(self):
        definition = {
            'id': self.node_id,
            'next_id': self.next_node_id,
            'empty_id': self.empty_node_id,
            'variable': self.variable,
            'count': self.sample_count,
            'avoid_repeats': self.avoid_repeats,
        }

        return json.dumps(definition, indent=2)

    def node_definition(self):
        node_def = super().node_definition() # pylint: disable=missing-super-argument

        node_def['empty_id'] = self.empty_node_id
        node_def['variable'] = self.variable
        node_def['avoid_repeats'] = self.avoid_repeats
        node_def['count'] = self.sample_count

        return node_def

    def evaluate(self, dialog, response=None, last_transition=None, extras=None, logger=None): # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument
        safety_plan = extras.get('plan_safe_safety_plan', None)

        reasons = safety_plan.fetch_reason_for_living(sample_count=self.sample_count, avoid_repeats=self.avoid_repeats)

        if len(reasons) == 0:
            transition = DialogTransition(new_state_id=self.empty_node_id)

            transition.metadata['reason'] = 'plan-safe-fetch-reasons-for-living-empty'
            transition.metadata['exit_actions'] = []

            return transition

        reason_objs = []

        for reason in reasons:
            reason_objs.append({
                'caption': reason.caption,
                'image_url': reason.image.url,
            })

        transition = DialogTransition(new_state_id=self.next_node_id)

        transition.metadata['reason'] = 'plan-safe-fetch-reasons-for-living'
        transition.metadata['exit_actions'] = [{
            'type': 'store-value',
            'key': self.variable,
            'value': reason_objs,
        }]

        return transition

    def actions(self):
        return []

    def next_nodes(self):
        nodes = [
            (self.next_node_id, 'Next',),
            (self.empty_node_id, 'No reasons available',),
        ]

        return nodes

class SendReasonsForLivingNode(BaseNode):
    @staticmethod
    def parse(dialog_def):
        if dialog_def['type'] == 'plan-safe-send-reasons-for-living':
            try:
                send_node = SendReasonsForLivingNode(dialog_def['id'], dialog_def['next_id'], dialog_def.get('message_template', None), dialog_def.get('seconds_between', 10), dialog_def.get('count', 0), dialog_def.get('mode', 'sequential'))

                return send_node
            except KeyError:
                traceback.print_exc()

        return None

    def __init__(self, node_id, next_node_id, message_template, seconds_between, sample_count, mode):# pylint: disable=too-many-arguments
        super(SendReasonsForLivingNode, self).__init__(node_id, node_id) # pylint: disable=super-with-arguments

        self.next_node_id = next_node_id
        self.message_template = message_template
        self.seconds_between = seconds_between
        self.mode = mode
        self.sample_count = sample_count

        if self.sample_count is None:
            self.sample_count = 0

        if self.mode is None:
            self.mode = 'sequential'

    def node_type(self):
        return 'plan-safe-send-reasons-for-living'

    def str(self):
        definition = {
            'id': self.node_id,
            'next_id': self.next_node_id,
            'message_template': self.message_template,
            'seconds_between': self.seconds_between,
            'count': self.sample_count,
            'mode': self.mode,
        }

        return json.dumps(definition, indent=2)

    def node_definition(self):
        node_def = super().node_definition() # pylint: disable=missing-super-argument

        node_def['message_template'] = self.message_template
        node_def['seconds_between'] = self.seconds_between
        node_def['count'] = self.sample_count
        node_def['mode'] = self.mode

        return node_def

    def evaluate(self, dialog, response=None, last_transition=None, extras=None, logger=None): # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument
        safety_plan = extras.get('plan_safe_safety_plan', None)

        if extras is None:
            extras = {}

        sample_count = safety_plan.reason_for_living.all().count()

        if self.sample_count > 0 and self.sample_count < sample_count:
            sample_count = self.sample_count

        reasons = safety_plan.fetch_reason_for_living(sample_count=sample_count, sequential=True)

        if self.mode == 'random':
            reasons = safety_plan.fetch_reason_for_living(sample_count=sample_count, avoid_repeats=False)
        elif self.mode == 'random_no_repeat':
            reasons = safety_plan.fetch_reason_for_living(sample_count=sample_count, avoid_repeats=True)

        if len(reasons) == 0:
            transition = DialogTransition(new_state_id=self.next_node_id)

            transition.metadata['reason'] = 'plan-safe-fetch-reasons-for-living-empty'
            transition.metadata['exit_actions'] = []

            return transition

        django_engine = engines["django"]

        exit_actions = []
        reason_index = 0

        for reason in reasons:
            reason_index += 1

            new_extras = dict(extras)

            new_extras['reason'] = {
                'caption': mark_safe(reason.caption), # nosec
                'index': reason_index,
            }

            logger.error('self.message_template: %s', self.message_template)
            logger.error('extras: %s', new_extras)

            template = django_engine.from_string('{{ reason.caption }}')

            if self.message_template is not None and len(self.message_template.strip()) > 0:
                template = django_engine.from_string(self.message_template)

            rendered_value = template.render(new_extras)

            logger.error('rendered_value: %s', rendered_value)

            action = {
                'type': 'echo',
                'message': rendered_value,
                'delay': (reason_index - 1) * self.seconds_between
            }

            if reason.image:
                action['media_url'] = settings.SITE_URL + reason.image.url

            exit_actions.append(action)

        # TODO: Add pause action that halts the dialog until all reasons have had a chance to get out.

        transition = DialogTransition(new_state_id=self.next_node_id)

        transition.metadata['reason'] = 'plan-safe-send-reasons-for-living'
        transition.metadata['exit_actions'] = exit_actions

        return transition

    def actions(self):
        return []

    def next_nodes(self):
        nodes = [
            (self.next_node_id, 'Next',),
        ]

        return nodes

class AddReasonsForLivingNode(BaseNode):
    @staticmethod
    def parse(dialog_def):
        if dialog_def['type'] == 'plan-safe-add-reason-for-living':
            try:
                add_reason_node = AddReasonsForLivingNode(dialog_def['id'], dialog_def['next_id'], dialog_def.get('caption_template', None), dialog_def.get('media_url_template', None))

                return add_reason_node
            except KeyError:
                traceback.print_exc()

        return None

    def __init__(self, node_id, next_node_id, caption_template, media_url_template):# pylint: disable=too-many-arguments
        super(AddReasonsForLivingNode, self).__init__(node_id, node_id) # pylint: disable=super-with-arguments

        self.next_node_id = next_node_id
        self.caption_template = caption_template
        self.media_url_template = media_url_template

    def node_type(self):
        return 'plan-safe-add-reason-for-living'

    def str(self):
        definition = {
            'id': self.node_id,
            'next_id': self.next_node_id,
            'caption_template': self.caption_template,
            'media_url_template': self.media_url_template,
        }

        return json.dumps(definition, indent=2)

    def evaluate(self, dialog, response=None, last_transition=None, extras=None, logger=None): # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument
        safety_plan = extras.get('plan_safe_safety_plan', None)

        if extras is None:
            extras = {}

        django_engine = engines["django"]

        caption_template = django_engine.from_string('{% autoescape off %}' +  self.caption_template + '{% endautoescape %}')

        caption = caption_template.render(extras)

        media_url_template = django_engine.from_string(self.media_url_template)

        media_url = media_url_template.render(extras)

        caption_lines = caption.splitlines()

        if len(caption_lines) > 1:
            used_media = False

            for caption_line in caption_lines:
                caption_line = caption_line.strip()

                if caption_line != '':
                    if used_media is False:
                        safety_plan.add_reasons_for_living_from_url(caption_line, media_url)
                    else:
                        safety_plan.add_reasons_for_living_from_url(caption_line, '')
        else:
            safety_plan.add_reasons_for_living_from_url(caption, media_url)

        transition = DialogTransition(new_state_id=self.next_node_id)

        transition.metadata['reason'] = 'plan-safe-add-reason-for-living'
        transition.metadata['exit_actions'] = []

        return transition

    def actions(self):
        return []

    def next_nodes(self):
        nodes = [
            (self.next_node_id, 'Next',),
        ]

        return nodes

class AddHelperMessageNode(BaseNode):
    @staticmethod
    def parse(dialog_def):
        if dialog_def['type'] == 'plan-safe-add-helper-message':
            try:
                add_helper_message_node = AddHelperMessageNode(dialog_def['id'], dialog_def['next_id'], dialog_def.get('helper_type', None), dialog_def.get('helper_name', None), dialog_def.get('helper_message', None))

                return add_helper_message_node
            except KeyError:
                traceback.print_exc()

        return None

    def __init__(self, node_id, next_node_id, helper_type, helper_name, helper_message):# pylint: disable=too-many-arguments
        super(AddHelperMessageNode, self).__init__(node_id, node_id) # pylint: disable=super-with-arguments

        self.next_node_id = next_node_id
        self.helper_type = helper_type
        self.helper_name = helper_name
        self.helper_message = helper_message

    def node_type(self):
        return 'plan-safe-add-helper-message'

    def str(self):
        definition = {
            'id': self.node_id,
            'next_id': self.next_node_id,
            'helper_type': self.helper_type,
            'helper_name': self.helper_name,
            'helper_message': self.helper_message,
        }

        return json.dumps(definition, indent=2)

    def evaluate(self, dialog, response=None, last_transition=None, extras=None, logger=None): # pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-statements, unused-argument
        safety_plan = extras.get('plan_safe_safety_plan', None)

        if extras is None:
            extras = {}

        name_template = '{% autoescape off %}' + self.helper_name + '{% endautoescape %}'

        helper_name = apply_template(name_template, extras)

        message_template = '{% autoescape off %}' + self.helper_message + '{% endautoescape %}'

        helper_message = apply_template(message_template, extras)

        safety_plan.add_helper_message(self.helper_type, helper_name, helper_message)

        transition = DialogTransition(new_state_id=self.next_node_id)

        transition.metadata['reason'] = 'plan-safe-add-helper-message'
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
        ('Plan Safe: Send Reasons For Living', 'plan-safe-send-reasons-for-living',),
        ('Plan Safe: Add Reason For Living', 'plan-safe-add-reason-for-living',),
        ('Plan Safe: Add Helper Message', 'plan-safe-add-helper-message',),
    ]


def identify_script_issues(script): # pylint: disable=unused-argument
    issues = []

    # TBD

    return issues

def fetch_destination_variables(destination):
    variables = {}

    participant_found = False

    for participant in Participant.objects.all():
        if participant.fetch_phone_number() == destination:
            participant_found = True

            variables['plan_safe_safety_plan_url'] = participant.get_absolute_url()

            variables['plan_safe_contact_card_url'] = 'https://%s%s' % (settings.ALLOWED_HOSTS[0], reverse('plan_safe_contact_card', args=[participant.login_token]))

            safety_plan = participant.safety_plans.order_by('-created').first()

            if safety_plan is None:
                safety_plan = SafetyPlan.objects.create(participant=participant)

            variables['plan_safe_safety_plan'] = safety_plan
            variables['safety_plan'] = safety_plan

            variables['crisis_lines'] = CrisisHelpLine.objects.all().order_by('order_label')

            variables['is_control'] = participant.metadata.get('is_control', False)
            variables['personal_url_enabled'] = (variables['is_control'] is False) # pylint: disable=superfluous-parens

    if participant_found is False:
        now = timezone.now()

        identifier = None

        while identifier is None or Participant.objects.filter(identifier=identifier).count() > 0:
            identifier = 'TESTING-%s' % get_random_string(length=8, allowed_chars='0123456789')

        metadata = {
            'note': 'Automatically created using testing interface, not regular enrollement.'
        }

        participant = Participant.objects.create(identifier=identifier, phone_number=destination, created=now, updated=now, metadata=metadata)

        return fetch_destination_variables(destination)

    return variables

def initialize_dialog(dialog):
    logger = logging.getLogger()

    if dialog.script is not None and 'embed-dialogs' in dialog.script.labels_list():
        embeds = ('safety-plan-now', 'menu-060525', 'automated-risk-management')

        original_nodes = dialog.dialog_snapshot

        for embed in embeds:
            embed_script = DialogScript.objects.filter(identifier=embed, embeddable=True).first()

            if embed_script is not None:
                machine = DialogMachine(embed_script.definition)

                prefix = '%s___%s__' % (dialog.script.identifier, embed_script.identifier)

                machine.prefix_nodes(prefix)

                embed_nodes = machine.dialog_definition()

                logger.error('initialize_dialog - nodes: %s', json.dumps(embed_nodes, indent=2))

                for node in embed_nodes:
                    if (node['type'] in ('begin', 'end',)) is False:
                        original_nodes.append(node)

        dialog.dialog_snapshot = original_nodes

        dialog.save()

def allow_session_nudge(session):
    session_dest = session.current_destination()

    for participant in Participant.objects.all():
        if participant.fetch_phone_number() == session_dest:
            now = participant.local_time(timezone.now())

            start = participant.local_time(datetime.datetime(now.year, now.month, now.day, hour=participant.day_start.hour, minute=participant.day_start.minute))
            end = participant.local_time(datetime.datetime(now.year, now.month, now.day, hour=participant.day_end.hour, minute=participant.day_end.minute))

            if start > end:
                end = end + datetime.timedelta(days=1)

            if (end - start).total_seconds() < (60 * 60 * settings.PLAN_SAFE_MINIMUM_WINDOW_HOURS): # 10 hours:
                end = start + datetime.timedelta(hours=10)

            if start <= now <= end:
                return True

            return False

    return True

def launch_keyword_enabled(sender, keyword): # pylint: disable=unused-argument
    definition = {}

    try:
        definition = json.loads(keyword.launch_condition)
    except json.JSONDecodeError:
        pass

    condition = definition.get('condition', None)

    if condition is not None:
        if condition == 'plan_safe_active':
            # Should be active all the time outside of dialogs.
            # Always want this accessible once people have gotten the safety plan
            # (i.e, control group as well but only once the plansafe part of the intervention is active).

            pass
        elif condition == 'in_blank_days':
            pass

    return True
