from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
TESTS_DIR = ROOT_DIR / 'tests'
WORKFLOWS_DIR = ROOT_DIR / 'workflows'
SRC_DIR = ROOT_DIR / 'recast-workflow'
INTERFACE_DIR = SRC_DIR / 'interfaces'
SUBWORKFLOWS_DIR = SRC_DIR / 'subworkflows'
IMAGES_DIR = SRC_DIR / 'images'
