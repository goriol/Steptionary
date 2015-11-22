import os
import json
from uuid import uuid4

ENCODING = 'utf-8'
STEPTIONARY_HOME = os.path.expanduser(os.path.join('~', '.steptionary'))
INDEX_FILENAME = os.path.join(STEPTIONARY_HOME, 'index.json')

class _Slow:

    index = {}

    def __init__(self):
        if not os.path.exists(STEPTIONARY_HOME):
            print('Creating plugin home')
            os.mkdir(STEPTIONARY_HOME)

        self._load()

    def _load(self):
        try:
            with open(INDEX_FILENAME, 'r', encoding = ENCODING) as f:
                self.index = json.load(f)
        except FileNotFoundError:
            print('Initializing cache index')
            self._save()


    def _retrieve(self, filename, create = False):
        if filename in self.index:
            id = self.index[filename]['cache']
            cache = os.path.join(STEPTIONARY_HOME, id)
            return cache

        if create == True:
            id = str(uuid4())
            self.index[filename] = {'cache': id}
            cache = os.path.join(STEPTIONARY_HOME, id)
            return cache

        return None

    def _save(self):
        with open(INDEX_FILENAME, 'w', encoding = ENCODING) as f:
            json.dump(self.index, f)

    def _update(self, filename):
        mtime = os.path.getmtime(filename)
        self.index[filename]['mtime'] = mtime
        self._save()

    def has(self, filename):
        if filename in self.index:
            cache_mtime = self.index[filename]['mtime']
            file_mtime = os.path.getmtime(filename)
            if file_mtime == cache_mtime:
                return True

        return False

    def get(self, filename):
        cache = self._retrieve(filename)
        with open(cache, 'r', encoding = ENCODING) as f:
            return json.load(f)

    def set(self, filename, content):
        cache = self._retrieve(filename, True)
        with open(cache, 'w', encoding = ENCODING) as f:
            json.dump(content, f)

        self._update(filename)

class _Fast:

    index = {}

    def has(self, filename):
        return filename in self.index

    def get(self, filename):
        return self.index[filename]

    def set(self, filename, content):
        self.index[filename] = content

class _Cache:

    def __init__(self):
        # Provide two cache levels:
        self.slow = _Slow()
        self.fast = _Fast()

    def has(self, filename):
        return self.slow.has(filename)

    def get(self, filename):
        if not self.fast.has(filename):
            self.fast.set(filename, self.slow.get(filename))

        return self.fast.get(filename)

    def set(self, filename, content):
        self.fast.set(filename, content)
        self.slow.set(filename, content)

# Make it a singleton
cache = _Cache()
