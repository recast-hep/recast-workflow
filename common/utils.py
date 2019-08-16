import os

import yaml

import definitions


def get_toplevel_path(step, workflow_name):
    return os.path.join(definitions.ROOT_DIR, step, workflow_name)


def get_workflow_path(step, workflow_name, environment_settings):
    #TODO: use given environment_settings.
    raise NotImplementedError()
    #return os.path.join(get_toplevel_path(step, workflow_name), 'workflow.yml')


def get_description(step, workflow_name):
    toplevel_path = get_toplevel_path(step, workflow_name)
    description_path = os.path.join(toplevel_path, 'description.yml')
    with open(description_path, 'r') as fd:
        description = yaml.full_load(fd)
    for d in description['inputs']:
        d.setdefault('optional', False)
    return description


def get_interface(interface_name):
    interface_path = os.path.join(
        definitions.INTERFACE_DIR, f'{interface_name}.yml')
    with open(interface_path, 'r') as fd:
        interface = yaml.full_load(fd)
    return interface

def get_translated_inputs(step, name, inputs):
    raise NotImplementedError()