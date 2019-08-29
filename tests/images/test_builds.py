import importlib
import os
from pathlib import Path

import definitions


def test_all_builds():
    for build_path in Path(definitions.ROOT_DIR, 'images').glob('**/build.py'):
        spec = importlib.util.spec_from_file_location('build', build_path)
        build_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_module)
        build_module.build()
