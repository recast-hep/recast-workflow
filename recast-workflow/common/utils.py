import json
import logging
import os
from pathlib import Path
from typing import Dict
from urllib.request import urlopen

import yaml

import definitions


def get_subworkflow_dir_path(step: str, subworkflow_name: str) -> Path:
    return definitions.SUBWORKFLOWS_DIR / step / subworkflow_name


def get_image_dir_path(step: str, subworkflow_name: str) -> Path:
    return definitions.IMAGES_DIR / step / subworkflow_name


def get_step_dir_path(step: str) -> Path:
    return definitions.SUBWORKFLOWS_DIR / step


def get_common_inputs_path(step: str) -> Path:
    return get_step_dir_path(step) / 'common_inputs.yml'


def get_common_inputs(step: str, include_descriptions=False) -> Dict[str, str]:
    """Returns the common inputs for the given step, along with their descriptions."""
    step_dir_path = get_step_dir_path(step)
    common_inputs_path = step_dir_path / 'common_inputs.yml'
    if not common_inputs_path.exists():
        return []
    with common_inputs_path.open() as f:
        if include_descriptions:
            return yaml.full_load(f)
        else:
            return yaml.full_load(f).keys()


def get_workflow_path(step, workflow_name, environment_settings):
    # TODO: use given environment_settings.
    raise NotImplementedError()
    # return os.path.join(get_toplevel_path(step, workflow_name), 'workflow.yml')


def get_description(step, workflow_name):
    toplevel_path = get_subworkflow_dir_path(step, workflow_name)
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


def translate_common_inputs(step, name, inputs):
    raise NotImplementedError()


def download_cds(cds_id):
    url = 'https://cds.cern.ch/record/{}/?of=recjson'.format(cds_id)
    return json.load(urlopen(url))


def extract_cds(cds_id, data):
    copnames = data[0]['corporate_name']

    collaboration = None
    for cop in copnames:
        if 'collaboration' in cop:
            collaboration = cop['collaboration']
    if not collaboration:
        for cop in copnames:
            if 'name' in cop:
                name = cop['name']
                if any([x in name for x in ['collaboration', 'Collaboration']]):
                    collaboration = name
    if not collaboration:
        raise RuntimeError('no collaboration in CDS record {}'.format(cds_id))

    title = data[0]['title']['title']
    abstracttext = data[0]['abstract']['summary']

    result = {
        'inspire_id': '',
        'collaboration': collaboration,
        'title': title,
        'abstract': abstracttext,
        'doi': '',
        'arXiv': '',
        'inspireURL': '',
        'pubtype': 'cds',
        'pubid': cds_id
    }
    verify_data(result)
    return result


def download_inspire(inspire_id):
    url = 'https://inspirehep.net/record/{}?of=recjson'.format(inspire_id)
    return json.load(urlopen(url))


def extract_inspire(inspire_id, data):
    url = 'http://inspirehep.net/record/{}'.format(inspire_id)
    abstract = data[0]['abstract']
    abstracttext = None
    if type(abstract) == dict and abstract['number'] == 'arXiv':
        abstracttext = abstract['summary']
    elif type(abstract) == list:
        for x in abstract:
            if x.get('number', '') == 'arXiv':
                abstracttext = x['summary']
    else:
        raise RuntimeError(
            'not sure how to find abstract for inspire %s', inspire_id)

    title = data[0]['title']['title']
    if type(data[0]['doi']) == list:
        doi = data[0]['doi'][0]
    elif type(data[0]['doi']) in [str]:
        doi = data[0]['doi']
    else:
        raise RuntimeError('weird doi', data[0]['doi'])

    collaboration = data[0]['corporate_name'][0]['collaboration']
    arXiv = [x['value'] for x in data[0]['system_control_number']
             if x['institute'] == 'arXiv'][0]
    inspire = url
    result = {
        'collaboration': collaboration,
        'title': title,
        'abstract': abstracttext,
        'doi': doi,
        'arXiv': arXiv,
        'inspireURL': inspire,
        'pubtype': 'inspire',
        'pubid': inspire_id
    }

    verify_data(result)
    return result


def verify_data(result):
    try:
        assert all([type(x) in [str] for x in result.values()])
    except AssertionError:
        logging.error('vvvvvv')
        for k, v in result.iteritems():
            logging.error(f'{k} {type(v)} {v}')
        raise RuntimeError('Type Problem')
