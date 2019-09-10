import json
import logging
import time
from typing import Dict

import requests

import definitions
from common import utils


def get_analyses():
    cache_path = definitions.CACHE_DIR / 'selection' / 'rivet' / 'analyses.json'
    if not cache_path.exists() or (time.time() - cache_path.stat().st_mtime) > 3600:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open('w+') as f:
            #TODO: handle requests error cases.
            f.write(requests.post('https://rivet.hepforge.org/analyses.json').text)
    with cache_path.open('r') as f:
        return json.load(f)


def is_valid(analysis_id: str) -> bool:
    return analysis_id in get_analyses()
