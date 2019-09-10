from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
TESTS_DIR = ROOT_DIR / 'tests'
WORKFLOWS_DIR = ROOT_DIR / 'workflows'
INTERFACE_DIR = SRC_DIR / 'interfaces'
SUBWORKFLOWS_DIR = SRC_DIR / 'subworkflows'
IMAGES_DIR = SRC_DIR / 'images'
CACHE_DIR = ROOT_DIR / 'cache'
