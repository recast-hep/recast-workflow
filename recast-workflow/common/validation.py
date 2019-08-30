import argparse
import os
from typing import Dict, List, Union

from common import utils


def get_missing_inputs(step: str, workflow_name: str, inputs: Dict[str, str], include_descriptions=False, include_optional=False) -> Union[List[str], Dict[str, str]]:
    """Returns a list of the inputs for workflow_name for the given step that are missing from the given inputs."""
    description = utils.get_description(step, workflow_name)
    common_inputs = utils.get_common_inputs(
        step, include_descriptions=include_descriptions)
    if include_descriptions:
        required_inputs = {e['name']: e['description']
                           for e in description['inputs'] if not e['optional'] or include_optional}
        required_inputs.update(common_inputs)
        missing_inputs = {
            k: v for k, v in required_inputs.items() if k not in inputs.keys()}
    else:
        required_inputs = [e['name'] for e in description['inputs']
                           if not e['optional'] or include_optional]
        required_inputs.extend(common_inputs)
        inputs = inputs.keys()
        missing_inputs = list(set(required_inputs).difference(set(inputs)))
    return missing_inputs


def get_invalid_inputs(step: str, workflow_name: str, inputs: Dict[str, str]) -> Dict[str, str]:
    """Returns a list of the elements from the given inputs that are invalid."""
    description = utils.get_description(step, workflow_name)
    common_inputs = utils.get_common_inputs(step)
    valid_inputs = set(common_inputs).union(
        set(e['name'] for e in description['inputs']))
    invalid_inputs = {k: v for k, v in inputs.items() if k not in valid_inputs}
    return invalid_inputs
