import argparse

import yaml

from common import utils, validation


def make_workflow_from_yaml(yaml_path, output_path=None):
    with open(yaml_path, 'r') as fd:
        yaml_text = yaml.full_load(fd)
    subworkflows = []
    
    return make_workflow(subworkflows, output_path)

def make_workflow(subworkflows, output_path=None):
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

        # Create parameters dict from inputs + interface.
        workflow_path = utils.get_workflow_path(step, name, environment_settings)
        description = utils.get_description(step, name)
        translated_inputs = utils.get_translated_inputs(step, name, inputs)
        parameters = {k: {'step': 'init', 'output': k} for k in translated_inputs}
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
    if output_path:
        with open('output_path', 'w+') as fd:
            yaml.dump(workflow, fd)
    return workflow

def main():
    parser = argparse.ArgumentParser(
        description='Make a complete workflow from sub-workflows.')
    parser.add_argument('make_workflow_yaml')
    parser.add_argument('output_path')
    args = parser.parse_args()
    make_workflow_from_yaml(args.make_workflow_yaml, args.output_path)

if __name__ == '__main__':
    main()
