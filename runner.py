import os
import threading

from Steptionary.reader import Reader

#
# Run time consuming tasks in a separate thread
#
class Runner(threading.Thread):

    def __init__(self, settings, target, timeout, callback):
        self.settings = settings
        self.target = target
        self.timeout = timeout
        self.callback = callback
        self.reader = Reader()
        threading.Thread.__init__(self)

    def get_feature_extensions(self):
        return self.settings.get('cucumber_feature_extensions')

    def get_folder_exclude_patterns(self):
        return self.settings.get('folder_exclude_patterns')

    def filter_features(self, folder, *args):
        files = []
        feature_extensions = self.get_feature_extensions()
        excluded = self.get_folder_exclude_patterns()
        for fn in os.listdir(folder):
            fqfn = os.path.join(folder, fn)
            if os.path.isfile(fqfn):
                name, extension = os.path.splitext(fqfn)
                if extension in feature_extensions:
                    files.append(fqfn)
            elif os.path.isdir(fqfn):
                if fn not in excluded:
                    files += self.filter_features(fqfn, *args)

        return files

    def read_feature(self, filename):
        steps = self.reader.get_steps(filename)
        self.callback(filename)

    def browse_folders(self, folders):
        for folder in folders:
            files = self.filter_features(folder)
            for filename in files:
                self.read_feature(filename)

    def run(self):
        if type(self.target) is list:
            self.browse_folders(self.target)
        else:
            self.read_feature(self.target)

    def stop(self):
        if self.isAlive():
            self._Thread__stop()
