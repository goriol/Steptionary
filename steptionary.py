import os
import sys
import sublime
import sublime_plugin

from functools import reduce

from Steptionary.persistence import save

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

lib_path = os.path.join(__path__, 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from gherkin3.parser import Parser
from gherkin3.token_scanner import TokenScanner
from gherkin3.errors import CompositeParserException

class ExampleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        parser = Parser()
        # Parse the whole buffer
        content = sublime.Region(0, self.view.size())
        feature = parser.parse(TokenScanner(self.view.substr(content)))
        pos = self.view.sel()[0].begin()
        print(feature['scenarioDefinitions'])
        print(pos)
        # self.view.replace(edit, content, feature.name)

def pluck(iterable, prop):
    return map(lambda item: item[prop], iterable)

class ParseOnSave(sublime_plugin.EventListener):
    def settings_get(self, name):
        plugin_settings = sublime.load_settings('Steptionary.sublime-settings')
        return plugin_settings.get(name)

    def strip_comments(self, step):
        comment = step.find('#')
        if comment != -1:
            return step[:comment].rstrip()
        return step

    def filter_steps(self, defs):
        f = lambda prev, curr: prev + list(map(self.strip_comments, pluck(curr['steps'], 'text')))
        return reduce(f, defs, [])

    def save_steps(self, filename, defs):
        steps = self.filter_steps(defs)
        save(filename, steps)

    def on_post_save_async(self, view):
        expected_extension = self.settings_get('cucumber_features_extension')
        filename, extension = os.path.splitext(view.file_name())

        if extension == expected_extension:
            parser = Parser()
            content = sublime.Region(0, view.size()) # Parse the whole buffer
            try:
                feature = parser.parse(TokenScanner(view.substr(content)))
                defs = feature['scenarioDefinitions']
                defs.append(feature['background'])
                self.save_steps(view.file_name(), defs)
            except CompositeParserException as e:
                print(e)
