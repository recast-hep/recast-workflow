import json
import logging
from typing import Dict

import definitions
from common import utils


def dump_rivet():
    rivetdata = json.load(open('rivet/analyses.json'))
    dumpdata = []

    for inspire_id, rivet_ids in rivetdata.items():
        if any([('ATLAS' in x) for x in rivet_ids]):
            logging.debug(inspire_id)
            data = utils.download_inspire(inspire_id)
            data = utils.extract_inspire(inspire_id, data)
            dumpdata.append(data)

    json.dump(dumpdata, open('rivet_dump.json', 'w'))


def is_valid() -> bool:
    pass
