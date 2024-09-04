# pylint: disable=no-member, line-too-long, fixme

import importlib
import json
import logging
import traceback

from django.conf import settings

from django_dialog_engine.dialog import BaseNode, DialogTransition, fetch_default_logger

from .models import GenerativeAIModel, GenerativeAIException

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
        self.value = value
        self.operation = operation

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
        # Update safety plan

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


def identify_script_issues(script): # pylint: disable=too-many-locals, too-many-branches
    issues = []

    # TBD

    return issues
