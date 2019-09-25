import argparse
import importlib
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

import definitions
from common import utils
from images import build_utils
from scripts import catalogue


def expand_workflow(workflow_path: Path, toplevel_path: Path):
    def replace_refs(yaml_obj):
        if type(yaml_obj) == dict:
            for k in yaml_obj:
                if k == '$ref':
                    return expand_workflow(toplevel_path / Path(yaml_obj[k]), toplevel_path)
                yaml_obj[k] = replace_refs(yaml_obj[k])
        elif type(yaml_obj) == list:
            for i, v in enumerate(yaml_obj):
                yaml_obj[i] = replace_refs(v)
        return yaml_obj
    with workflow_path.open() as f:
        yaml_obj = yaml.safe_load(f)
    return replace_refs(yaml_obj)


def make_workflow_dir():
    if not definitions.WORKFLOWS_DIR.exists():
        definitions.WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix='workflow-', dir=definitions.WORKFLOWS_DIR))


def make_subworkflow(step: str, subworkflow_name: str, environment_settings: Dict[str, str]) -> Dict:
    """Creates a yadage workflow for the given subworkflow with the given environment settings.

    If make.py exists in the corresponding subworkflow directory, it is run with the assumption that it will handle making the subworkflow.
    Otherwise, workflow.py in the subworkflow directory is expanded using jsonref and any environment variables enclosed in braces are replaced with the corresponding value in environment_settings.

    Returns:
        A dict representing the contents of a yaml file that specifies a yadage workflow.
    """
    source_path = utils.get_subworkflow_dir_path(step, subworkflow_name)
    make_path = source_path / 'make.py'
    if make_path.exists():
        spec = importlib.util.spec_from_file_location('make', make_path)
        make_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(make_module)
        subworkflow = make_module.make(environment_settings)
    else:
        # Add environment settings to the copied yaml files.
        used_settings = set()
        subworkflow_path = source_path / 'workflow.yml'
        subworkflow = expand_workflow(
            subworkflow_path, subworkflow_path.parent)
        valid_settings = {}
        text = yaml.dump(subworkflow)
        for k, v in environment_settings.items():
            if f'{{k}}' in text:
                valid_settings[k] = v
        valid_settings = {
            k: v for k, v in environment_settings.items() if f'{{k}}' in text}
        text = text.format(**valid_settings)
        used_settings.update(valid_settings.keys())
        unused_settings = set(environment_settings.keys()
                              ).difference(used_settings)
        if len(unused_settings) != 0:
            raise ValueError(
                f'The following environment settings were provided but not used: {unused_settings}')
        subworkflow = yaml.safe_load(text)
    
    return subworkflow


def build_subworkflow(step: str, name: str, environment_settings: dict):
    """Builds the images corresponding to the given subworkflow and environment settings.

    The subworkflow's base image directory is searched recursively for dockerfiles. Each directory with a dockerfile is assumed to correspond to an image, where the name of the directory is equivalent to the name of the image.
    If a build.py exists in an image directory, it is run and assumed to handle building the image. Otherwise, the 'build_tags' section of the description.yml for the subworkflow is checked for an appropriate tag.
    It is assumed that this tag is also the build arg for the image creation, and a corresponding docker build and push are run.
    """
    subworkflow_dir_path = utils.get_image_dir_path(step, name)
    description = utils.get_subworkflow_description(step, name)

    dir_paths = [p.parent for p in subworkflow_dir_path.rglob('Dockerfile')]
    used_environment_settings = set()
    ran_build_script = False
    for dir_path in dir_paths:
        build_script_path = dir_path / 'build.py'
        if build_script_path.exists():
            spec = importlib.util.spec_from_file_location(
                'build', build_script_path)
            build_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(build_module)
            build_module.build(environment_settings)
            ran_build_script = True
        else:
            image_name = dir_path.name
            if 'build' in description and image_name in description['build']:
                tag_name = description['build'][image_name]
                if tag_name not in environment_settings:
                    raise ValueError(
                        f"Invalid environment_settings: description.yml's build field indicates that '{tag_name}' should be present, but it is not.")
                tag = environment_settings[tag_name]
                build_args = {tag_name: tag}
                image_id = f'recast/{image_name}:{tag}'
                used_environment_settings.add(tag_name)
            else:
                build_args = None
                image_id = f'recast/{image_name}:latest'
            build_utils.build(image_id, dir_path, build_args)

    unused_environment_settings = set(
        environment_settings.keys()).difference(used_environment_settings)
    if len(unused_environment_settings) > 0 and not ran_build_script:
        raise ValueError(
            f'The following environment settings were provided but were unused: {unused_environment_settings}.')
    elif len(unused_environment_settings) > 0 and ran_build_script:
        logging.warning(
            f'The following environment settings were provided but were unused in default image building: {unused_environment_settings}. However, a custom build.py was run for one or more images, so this may be a false alarm.')


def make_workflow_from_yaml(yaml_path: Path):
    with yaml_path.open() as fd:
        yaml_obj = yaml.safe_load(fd)

    steps = yaml_obj['steps']
    names = yaml_obj['names']
    environment_settings = yaml_obj['environment_settings']

    return make_workflow(steps, names, environment_settings)


def make_workflow(steps: List[str], names: List[str], environment_settings: List[Dict[str, str]]) -> Dict:
    """Creates a yadage workflow using the given subworkflow specifications. 

    Args:
        steps: A list of the subworkflow steps for each subworkflow.
        names: A list of the subworkflow names for each subworkflow.
        environment_settings: A list of dicts mapping environment setting names to values for each subworkflow.

    Returns:
        A dict representing the contents of a yaml file that specifies a yadage workflow."""

    workflow = {'stages': []}
    for i, (step, name, sub_environment_settings) in enumerate(zip(steps, names, environment_settings)):
        # Validate the environment settings.
        invalid_environment_settings = set(sub_environment_settings.keys()).difference(
            set(catalogue.get_environment_settings(step, name)))
        if len(invalid_environment_settings) > 0:
            raise ValueError(
                f'Environment settings for subworkflow {name} from step {step} contains the following invalid parameters (not listed in the associated description.yml): {invalid_environment_settings}')

        # Build the image if necessary.
        build_subworkflow(step, name, sub_environment_settings)

        # Create parameters dict from inputs + interface.
        subworkflow = make_subworkflow(
            step, name, sub_environment_settings)
        description = utils.get_subworkflow_description(step, name)
        inputs = catalogue.get_missing_inputs(step, name, {})
        parameters = {k: {'step': 'init', 'output': k}
                      for k in inputs}
        interfaces = description['interfaces']
        if 'input' in interfaces:
            interface = utils.get_interface(interfaces['input'][0])
            for parameter in interface['parameters']:
                if parameter['name'] in parameters:
                    raise ValueError(
                        f'interface {interfaces["input"]} has a parameter {parameter["name"]} that conflicts with a parameter for workflow {name} for step {step}.')
                parameters[parameter['name']] = {
                    'step': steps[i-1], 'output': parameter['name']}
        # Write the rest of the yaml.
        scheduler = {'scheduler_type': 'singlestep-stage',
                     'parameters': parameters, 'workflow': subworkflow}
        dependencies = ['init']
        if i > 0:
            dependencies.append(f'{steps[i-1]}_{names[i-1]}')
        workflow['stages'].append(
            {'name': f'{step}_{name}', 'dependencies': dependencies, 'scheduler': scheduler})

    return workflow


def run_make(args):
    make_workflow_from_yaml(Path(args.spec))


def main():
    parser = argparse.ArgumentParser(
        description='Make a complete workflow from sub-workflows.')
    subparsers = parser.add_subparsers()
    make_parser = subparsers.add_parser(
        'make', help='Make a workflow from subworkflows.')
    make_parser.add_argument(
        'spec', help='yaml file describing the subworkflows that will be used.')
    build_parser = subparsers.add_parser(
        'build', help='Build a particular subworkflow (useful for development).')
    build_parser.add_argument(
        'step', help='The step the subworkflow fulfills.')
    build_parser.add_argument('name', help='The name of the subworkflow.')

    parser.add_argument('make_workflow_yaml')
    args = parser.parse_args()
    workflow_dir = make_workflow_from_yaml(args.make_workflow_yaml)
    print(f'Workflow in {workflow_dir}.')


if __name__ == '__main__':
    main()
