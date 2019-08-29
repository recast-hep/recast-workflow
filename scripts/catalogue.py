import importlib
import logging
from collections import defaultdict
from typing import Dict, List

import yaml

from common import utils


def query(common_inputs: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
    """Given values for common inputs for some steps, returns the subworkflows for each of those steps that supports those values.

    Each subworkflow for the given steps is assumed to implement a common_inputs.py file with an is_valid(common_inputs: Dict[str, str]) -> bool function.
    This function is called for each subworkflow to determine whether it should be included.

    Args:
        common_inputs: A dict where each key-value pair is of the form (step, step_inputs), where step_inputs is a dict mapping step input names to values.

    Returns:
        A dict where each key-value pair is of the form (step, allowed_subworkflows), where allowed_subworkflows is a list of the subworkflows for step that are allowed given the common inputs.
    """

    allowed = defaultdict(list)
    for step, step_inputs in common_inputs.items():
        # Verify that the input names are valid.
        common_inputs = utils.get_common_inputs(step)
        if not common_inputs:
            raise ValueError(
                f'common inputs {step_inputs} were provided for {step}, but {step} has no common inputs.')
        invalid_inputs = set(step_inputs.keys()).difference(common_inputs)
        if invalid_inputs:
            raise ValueError(
                f'common inputs {invalid_inputs} were provided for {step}, but these are not defined in common_inputs.yml for {step}.')
        # Ask each subworkflow whether it should be included.
        step_dir_path = utils.get_step_dir_path(step)
        subworkflow_dir_paths = [
            d for d in step_dir_path.glob('*') if d.is_dir()]
        for subworkflow_dir_path in subworkflow_dir_paths:
            common_inputs_script_path = subworkflow_dir_path / 'common_inputs.py'
            if not common_inputs_script_path.exists():
                raise RuntimeError(
                    f'Subworkflow {subworkflow_dir_path.name} for step {step} is missing common_inputs.py.')
            try:
                spec = importlib.util.spec_from_file_location(
                    'common_inputs', common_inputs_script_path)
                common_inputs_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(common_inputs_module)
                if common_inputs_module.is_valid(step_inputs):
                    allowed[step].append(subworkflow_dir_path.name)
            except Exception:
                logging.error(
                    f'Subworkflow {subworkflow_dir_path.name} for step {step} has an invalid common_inputs.py.')
                raise

    return allowed
