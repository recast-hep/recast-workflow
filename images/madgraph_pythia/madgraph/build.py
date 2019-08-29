import os

from images import build_utils


def build(madgraph_version=None):
    if madgraph_version:
        tag = f'recast/madgraph:{madgraph_version}'
        build_args = {'MADGRAPH_VERSION': madgraph_version}
    else:
        tag = 'recast/madgraph:default'
        build_args = None
    dir_path = os.path.dirname(os.path.realpath(__file__))
    build_utils.build(tag, dir_path, build_args)
