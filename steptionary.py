import os
import logging
import sublime
import sublime_plugin

from Steptionary.cache import cache
from Steptionary.runner import Runner

FEATURES = 'features'
STEPS = 'steps'

#
# Dictionary of step definitions
#
class Steptionary:

    dictionaries = {}
    running_thread = None

    def refresh_steps(self, dictionary):
        l = []
        for f in dictionary[FEATURES]:
            l += cache.get(f)

        dictionary[STEPS] = list(set(l))

    # Initialize window's dictionary
    def init(self, id):
        self.dictionaries[id] = {STEPS: [], FEATURES: []}

    # Add feature to the window's dictionary
    def add(self, id, filename):
        dictionary = self.dictionaries[id]
        if filename not in dictionary[FEATURES]:
            s = set(dictionary[FEATURES])
            s.add(filename)
            dictionary[FEATURES] = list(s)

        self.refresh_steps(dictionary)

    # Update steps only if the dictionary contains this feature
    def update(self, id, filename):
        dictionary = self.dictionaries[id]
        if filename in dictionary[FEATURES]:
            self.refresh_steps(dictionary)

    def setup(self, id, folders):
        def callback(filename):
            self.add(id, filename)

        self.init(id)
        if self.running_thread != None:
            self.running_thread.stop()

        self.running_thread = Runner(settings, folders, 30, callback)
        self.running_thread.start()

    def update_all(self, filename):
        def callback(filename):
            for id in self.dictionaries.keys():
                self.update(id, filename)

        if self.running_thread != None:
            self.running_thread.stop()

        self.running_thread = Runner(settings, filename, 30, callback)
        self.running_thread.start()

    def get_completions(self, id, prefix):
        steps = self.dictionaries[id][STEPS]
        completions = [(e,) * 2 for e in steps if e.find(prefix) != -1]
        return completions

    def is_feature(self, filename):
        name, extension = os.path.splitext(filename)
        if extension in settings.get('cucumber_feature_extensions'):
            return True

        return False

#
# Interface with Sublime Text
#
class Plugin(Steptionary, sublime_plugin.EventListener):

    # Use this event to emulate the missing on_window_activated(window)
    def on_activated(self, view):
        window = view.window()
        if window.id() not in self.dictionaries:
            self.setup(window.id(), window.folders())

    # on_post_save_async(view) is not available in ST2.
    # Use on_post_save(view) with threading instead.
    def on_post_save(self, view):
        filename = view.file_name()
        if self.is_feature(filename):
            self.update_all(filename)

    def on_query_completions(self, view, prefix, locations):
        if self.is_feature(view.file_name()):
            return (self.get_completions(view.window().id(), prefix), sublime.INHIBIT_WORD_COMPLETIONS & sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        return None

#
# Plugin initialization
#
def plugin_loaded():
    global settings
    settings = sublime.load_settings('Steptionary.sublime-settings')

# ST2 backward compatibility
if int(sublime.version()) < 3000:
    sublime.set_timeout(lambda: plugin_loaded(), 0)
