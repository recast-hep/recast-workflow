import importlib
import logging
from collections import defaultdict
from typing import Dict, List, OrderedDict

import yaml

import definitions
from common import utils
import itertools

def query(common_inputs: Dict[str, str]) -> List[OrderedDict[str, str]]:
    """Given values for common inputs, returns all combinations of subworkflows that support those values.

    Each common input should be defined in recast-workflow/common_inputs.yml, in which it is associated with a set of steps. 
    Each subworkflow for those steps is assumed to implement a common_inputs.py file with an is_valid() -> bool function.
    This function is called for each subworkflow to determine whether it should be included.

    Once the set of allowed subworkflows for these steps is determined, the set of all possible combinations is generated using the interfaces listed in description.yml for each subworkflow.

    Args:
        common_inputs: A dict where each key-value pair is of the form (input name, input value).

    Returns:
        A list of ordered dictionaries, where each ordered dictionary has key-value pairs of the form (step, subworkflow) which describe one possible subworkflow combination that is valid for the given common inputs.
    """

    allowed = defaultdict(list)
    descriptions = utils.get_common_inputs(include_descriptions=True)
    invalid_inputs = set(common_inputs.keys()).difference(
        descriptions.keys())
    if invalid_inputs:
        raise ValueError(
            f'common inputs {invalid_inputs} were provided, but these are not defined in common_inputs.yml.')

    steps = set(itertools.chain(descriptions[k]['steps'] for k in common_inputs))
    for step in steps:
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
                if common_inputs_module.is_valid(**{k: v for k,v in common_inputs.items() if k in common_inputs_module.is_valid.func_code.co_varnames}):
                    allowed[step].append(subworkflow_dir_path.name)
            except Exception:
                logging.error(
                    f'Subworkflow {subworkflow_dir_path.name} for step {step} has an invalid common_inputs.py.')
                raise

    return allowed
