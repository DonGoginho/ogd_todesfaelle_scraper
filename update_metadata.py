# -*- coding: utf-8 -*-
"""Update metadata (dateLastUpdated) on a CKAN dataset.

Usage:
  update_metadata.py -d <dataset-name> [--no-verify]
  update_metadata.py (-h | --help)

Options:
  -h, --help                    Show this screen.
  -d, --dataset <dataset-name>  Name of the CKAN dataset.
  --no-verify                   Disable SSL verification.
"""

import os
import sys
import traceback
from datetime import datetime

import pytz
import requests
from ckanapi import RemoteCKAN, NotFound
from docopt import docopt

arguments = docopt(__doc__, version='Update metadata on CKAN 1.0')

try:
    BASE_URL = os.getenv('CKAN_BASE_URL')
    API_KEY = os.getenv('CKAN_API_KEY')
    SSL_VERIFY = os.getenv('SSL_VERIFY')

    session = requests.Session()
    if SSL_VERIFY == "true":
        session.verify = True
    elif SSL_VERIFY == "false":
        session.verify = False
    else:
        session.verify = not arguments['--no-verify']

    ckan = RemoteCKAN(BASE_URL, session=session, apikey=API_KEY)

    dataset = arguments['--dataset']
    now_utc = pytz.utc.localize(datetime.utcnow())
    now_cet = now_utc.astimezone(pytz.timezone("Europe/Zurich"))

    data = {
        'id': dataset,
        'dateLastUpdated': now_cet.date().strftime('%d.%m.%Y'),
    }
    print(f"Updating metadata on dataset {dataset}: dateLastUpdated={data['dateLastUpdated']}")

    try:
        ckan.call_action('package_patch', data)
    except NotFound:
        print('Dataset %s not found!' % dataset, file=sys.stderr)
        raise
except Exception as e:
    print("Error: %s" % e, file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    sys.exit(1)
