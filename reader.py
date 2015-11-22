import os
import sys

from functools import reduce
from Steptionary.cache import cache

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

lib_path = os.path.join(__path__, 'lib')
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from gherkin3.parser import Parser
from gherkin3.token_scanner import TokenScanner
from gherkin3.errors import CompositeParserException

GHERKIN_SCENARIOS = 'scenarioDefinitions'
GHERKIN_BACKGROUND = 'background'
GHERKIN_STEPS = 'steps'
GHERKIN_TEXT = 'text'
GHERKIN_COMMENT = '#'

def pluck(iterable, prop):
    return map(lambda item: item[prop], iterable)

class Reader:

    def __init__(self):
        self.parser = Parser()

    def strip_comments(self, step):
        comment = step.find(GHERKIN_COMMENT)
        if comment != -1:
            return step[:comment].rstrip()
        return step

    def filter_definitions(self, defs):
        f = lambda prev, curr: prev + list(map(self.strip_comments, pluck(curr['steps'], 'text')))
        return reduce(f, defs, [])

    def read_steps(self, filename):
        try:
            feature = self.parser.parse(TokenScanner(filename))
            defs = []
            if GHERKIN_SCENARIOS in feature: defs += feature[GHERKIN_SCENARIOS]
            if GHERKIN_BACKGROUND in feature: defs.append(feature[GHERKIN_BACKGROUND])
            steps = self.filter_definitions(defs)
            cache.set(filename, steps)
        except CompositeParserException as e:
            steps = []
            print(e)

        return steps

    def get_steps(self, filename):
        if cache.has(filename):
            return cache.get(filename)

        return self.read_steps(filename)
