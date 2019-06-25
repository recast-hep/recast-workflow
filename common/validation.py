import argparse
import os

from common import utils


def get_missing_inputs(step, workflow_name, inputs):
    """Returns a list of the required inputs for workflow_name for the given step that are missing from the given inputs."""
    description = utils.get_description(step, workflow_name)
    missing_inputs = [e for e in description['inputs']
                      if not e['optional'] and e['name'] not in inputs.keys()]
    return missing_inputs


def get_invalid_inputs(step, workflow_name, inputs):
    """Returns a list of the elements from the given inputs that are invalid."""
    description = utils.get_description(step, workflow_name)
    invalid_inputs = [e for e in inputs if e not in [d['name']
                                                     for d in description['inputs']]]
    return invalid_inputs
