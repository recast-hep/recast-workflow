import argparse
import importlib
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path

import yaml

import definitions
from common import utils, validation
from images import build_utils


def make_workflow_dir():
    return tempfile.mkdtemp(suffix='workflow-', dir=definitions.WORKFLOWS_DIR)


def make_subworkflow(step: str, subworkflow_name: str, environment_settings: dict, toplevel_path: Path) -> Path:
    """Creates a directory in toplevel_path that contains the given subworkflow with the specified environment settings.

    If make.py exists in the corresponding subworkflow directory, it is run with the assumption that it will handle making the subworkflow. 
    Otherwise, all files in the subworkflow directory are copied and any environment variables enclosed in braces are replaced with the corresponding value in environment_settings.

    Returns:
        The path of the created subworkflow directory.
    """

    # TODO: verify that environment_settings is consistent with description.yml.
    dest_path = toplevel_path / step / subworkflow_name
    dest_path.mkdir()
    source_path = utils.get_subworkflow_dir_path(step, subworkflow_name)
    make_path = source_path / 'make.py'
    if make_path.exists():
        spec = importlib.util.spec_from_file_location('make', make_path)
        make_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(make_module)
        make_module.make(environment_settings, dest_path)
    else:
        shutil.copytree(source_path, dest_path)
        # Add environment settings to the copied yaml files.
        used_settings = set()
        for p in dest_path.rglob('*.yml'):
            with p.open() as f:
                text = yaml.full_load(f)
                valid_settings = {}
                breakpoint()
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

        return dest_path


def build_subworkflow(step: str, name: str, environment_settings: dict):
    """Builds the images corresponding to the given subworkflow and environment settings.

    The subworkflow's base image directory is searched recursively for dockerfiles. Each directory with a dockerfile is assumed to correspond to an image, where the name of the directory is equivalent to the name of the image.
    If a build.py exists in an image directory, it is run and assumed to handle building the image. Otherwise, the 'build_tags' section of the description.yml for the subworkflow is checked for an appropriate tag.
    It is assumed that this tag is also the build arg for the image creation, and a corresponding docker build and push are run.
    """
    subworkflow_dir_path = utils.get_image_dir_path(step, name)
    description = utils.get_description(step, name)

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


def make_workflow_from_yaml(yaml_path, output_path=None):
    raise NotImplementedError()
    with open(yaml_path, 'r') as fd:
        yaml_text = yaml.full_load(fd)
    
    subworkflows = []

    return make_workflow(subworkflows)


def make_workflow(subworkflows: list) -> Path:
    """Creates a directory that contains a workflow specified by the given subworkflows list. 

    Args:
        subworkflows: A list of the subworkflows. Each element should be a tuple of (step, name, inputs, environment_settings).

    Returns:
        A path to the directory that contains the workflow. The caller is responsible for cleaning up the directory after it has been used."""

    toplevel_path = make_workflow_dir()
    workflow = {'stages': []}
    for i, (step, name, inputs, environment_settings) in enumerate(subworkflows):
        # Validate the inputs.
        missing_inputs = validation.get_missing_inputs(step, name, inputs)
        if len(missing_inputs) > 0:
            raise ValueError(
                f'subworkflow {name} for step {step} has missing inputs. The following inputs are missing: {missing_inputs}')
        invalid_inputs = validation.get_invalid_inputs(step, name, inputs)
        if len(invalid_inputs) > 0:
            raise ValueError(
                f'subworkflow {name} for step {step} has invalid inputs. The following inputs are invalid: {invalid_inputs}')

        # Validate the environment settings.
        # TODO

        # Build the image.
        build_subworkflow(step, name, environment_settings)

        # Create parameters dict from inputs + interface.
        workflow_path = make_subworkflow(
            step, name, environment_settings, toplevel_path)
        description = utils.get_description(step, name)
        parameters = {k: {'step': 'init', 'output': k}
                      for k in inputs}
        interfaces = description['interfaces']
        if 'input' in interfaces:
            interface = utils.get_interface(interfaces['input'])
            for parameter in interface['parameters']:
                if parameter['name'] in parameters:
                    raise ValueError(
                        f'interface {interfaces["input"]} has a parameter {parameter["name"]} that conflicts with a parameter for workflow {name} for step {step}.')
                parameters[parameter['name']] = {
                    'step': subworkflows[i-1].step, 'output': parameter['name']}
        # Write the rest of the yaml.
        scheduler = {'scheduler_type': 'singlestep-stage',
                     'parameters': parameters, 'workflow': {'$ref': workflow_path}}
        dependencies = ['init']
        if i > 0:
            dependencies.append(subworkflows[i-1].subworkflow)
        workflow['stages'].append(
            {'name': name, 'dependencies': dependencies, 'scheduler': scheduler})
            
    return toplevel_path


def main():
    parser = argparse.ArgumentParser(
        description='Make a complete workflow from sub-workflows.')
    parser.add_argument('make_workflow_yaml')
    parser.add_argument('output_path')
    args = parser.parse_args()
    make_workflow_from_yaml(args.make_workflow_yaml, args.output_path)


if __name__ == '__main__':
    main()
