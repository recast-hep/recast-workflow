import os

from images import build_utils


def build(pythia_version=None):
    if pythia_version:
        tag = f'recast/pythia:{pythia_version}'
        build_args = {'PYTHIA_VERSION': pythia_version}
    else:
        tag = 'recast/pythia:default'
        build_args = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    build_utils.build(tag, dir_path, build_args)
