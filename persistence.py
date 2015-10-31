import os
import json
from uuid import uuid4

ENCODING = 'utf-8'
STEPTIONARY_HOME = os.path.expanduser(os.path.join('~', '.steptionary'))
INDEX_FILENAME = os.path.join(STEPTIONARY_HOME, 'index.json')

def init():
    print('Creating repository')
    os.mkdir(STEPTIONARY_HOME)

def _save_index():
    with open(INDEX_FILENAME, 'w', encoding = ENCODING) as f:
        json.dump(index, f)

def _update_index(cache_filename, filename):
    mtime = os.path.getmtime(cache_filename)
    index[filename]['mtime'] = mtime
    _save_index()

def save(filename, content):
    if filename in index:
        cache_id = index[filename]['cache']
    else:
        cache_id = str(uuid4())
        index[filename] = {'cache': cache_id}

    cache_filename = os.path.join(STEPTIONARY_HOME, cache_id)
    with open(cache_filename, 'w') as f:
        json.dump(content, f)
    _update_index(cache_filename, filename)

if not os.path.exists(STEPTIONARY_HOME):
    init()

index = {'version': 1}
try:
    with open(INDEX_FILENAME, 'r', encoding = ENCODING) as f:
        index = json.load(f)
except FileNotFoundError:
    print('Initializing repository')
    _save_index()
