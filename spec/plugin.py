import doctest
import os
import re
import types
import sys
import time
import traceback
import unittest
from StringIO import StringIO
from functools import partial

# Python 2.7: _WritelnDecorator moved.
try:
    from unittest import _WritelnDecorator
except ImportError:
    from unittest.runner import _WritelnDecorator

# Python 2.7: nose uses unittest's builtin SkipTest class
try:
    SkipTest = unittest.case.SkipTest
except AttributeError:
    SkipTest = nose.SkipTest


import nose
from nose.plugins import Plugin


################################################################################
## Functions for constructing specifications based on nose testing objects.
################################################################################

def dispatch_on_type(dispatch_table, instance):
    for type, func in dispatch_table:
        if type is True or isinstance(instance, type):
            return func(instance)


def remove_leading(needle, haystack):
    """Remove leading needle string (if exists).

    >>> remove_leading('Test', 'TestThisAndThat')
    'ThisAndThat'
    >>> remove_leading('Test', 'ArbitraryName')
    'ArbitraryName'
    """
    if haystack[:len(needle)] == needle:
        return haystack[len(needle):]
    return haystack


def remove_trailing(needle, haystack):
    """Remove trailing needle string (if exists).

    >>> remove_trailing('Test', 'ThisAndThatTest')
    'ThisAndThat'
    >>> remove_trailing('Test', 'ArbitraryName')
    'ArbitraryName'
    """
    if haystack[-len(needle):] == needle:
        return haystack[:-len(needle)]
    return haystack


def remove_leading_and_trailing(needle, haystack):
    return remove_leading(needle, remove_trailing(needle, haystack))


def camel2word(string):
    """Covert name from CamelCase to "Normal case".

    >>> camel2word('CamelCase')
    'Camel case'
    >>> camel2word('CaseWithSpec')
    'Case with spec'
    """
    def wordize(match):
        return ' ' + match.group(1).lower()

    return string[0] + re.sub(r'([A-Z])', wordize, string[1:])


def complete_english(string):
    """
    >>> complete_english('dont do this')
    "don't do this"
    >>> complete_english('doesnt is matched as well')
    "doesn't is matched as well"
    """
    for x, y in [("dont", "don't"),
                ("doesnt", "doesn't"),
                ("wont", "won't"),
                ("wasnt", "wasn't")]:
        string = string.replace(x, y)
    return string


def underscore2word(string):
    return string.replace('_', ' ')


def argumentsof(test):
    if test.arg:
        if len(test.arg) == 1:
            return " for %s" % test.arg[0]
        else:
            return " for %s" % (test.arg,)
    return ""


def underscored2spec(name):
    return complete_english(underscore2word(remove_trailing('_test', remove_leading('test_', name))))


def camelcase2spec(name):
    return camel2word(
        remove_trailing('_',
            remove_leading_and_trailing('Test', name)))


def camelcaseDescription(object):
    description = object.__doc__ or camelcase2spec(object.__name__)
    return description.strip()


def underscoredDescription(object):
    return object.__doc__ or underscored2spec(object.__name__).capitalize()


def doctestContextDescription(doctest):
    return doctest._dt_test.name


def noseMethodDescription(test):
    return test.method.__doc__ or underscored2spec(test.method.__name__)


def unittestMethodDescription(test):
    if test._testMethodDoc is None:
        return underscored2spec(test._testMethodName)
    else:
        description = test._testMethodDoc.split("\n")
        return "".join([text.strip() for text in description])


def noseFunctionDescription(test):
    # Special case for test generators.
    if test.descriptor is not None:
        if hasattr(test.test, 'description'):
            return test.test.description
        return "holds for %s" % ', '.join(map(str, test.arg))
    return test.test.func_doc or underscored2spec(test.test.func_name)


# Different than other similar functions, this one returns a generator
# of specifications.
def doctestExamplesDescription(test):
    for ex in test._dt_test.examples:
        source = ex.source.replace("\n", " ")
        want = None
        if '#' in source:
            source, want = source.rsplit('#', 1)
        elif ex.exc_msg:
            want = "throws \"%s\"" % ex.exc_msg.rstrip()
        elif ex.want:
            want = "returns %s" % ex.want.replace("\n", " ")

        if want:
            yield "%s %s" % (source.strip(), want.strip())


def testDescription(test):
    supported_test_types = [
        (nose.case.MethodTestCase, noseMethodDescription),
        (nose.case.FunctionTestCase, noseFunctionDescription),
        (doctest.DocTestCase, doctestExamplesDescription),
        (unittest.TestCase, unittestMethodDescription),
    ]
    return dispatch_on_type(supported_test_types, test.test)


def contextDescription(context):
    supported_context_types = [
        (types.ModuleType, underscoredDescription),
        (types.FunctionType, underscoredDescription),
        (doctest.DocTestCase, doctestContextDescription),
        # Handle both old and new style classes.
        (types.ClassType, camelcaseDescription),
        (type, camelcaseDescription),
    ]
    return dispatch_on_type(supported_context_types, context)


def testContext(test):
    # Test generators set their own contexts.
    if isinstance(test.test, nose.case.FunctionTestCase) \
           and test.test.descriptor is not None:
        return test.test.descriptor
    # So do doctests.
    elif isinstance(test.test, doctest.DocTestCase):
        return test.test
    else:
        return test.context


################################################################################
## Output stream that can be easily enabled and disabled.
################################################################################

class OutputStream(_WritelnDecorator):
    def __init__(self, on_stream, off_stream):
        self.capture_stream = StringIO()
        self.on_stream = on_stream
        self.off_stream = off_stream
        self.stream = on_stream

    def on(self):
        self.stream = self.on_stream

    def off(self):
        self.stream = self.off_stream

    def capture(self):
        self.capture_stream.truncate()
        self.stream = self.capture_stream

    def get_captured(self):
        self.capture_stream.seek(0)
        return self.capture_stream.read()


class SpecOutputStream(OutputStream):
    def print_text(self, text):
        self.on()
        self.write(text)
        self.off()

    def print_line(self, line=''):
        self.print_text(line + "\n")

    def print_context(self, context):
        self.print_line("\n%s" % contextDescription(context))

    def print_spec(self, color_func, test, status=None):
        spec = testDescription(test)
        if not isinstance(spec, types.GeneratorType):
            spec = [spec]
        for s in spec:
            name = "- %s" % s
            paren = (" (%s)" % status) if status else ""
            self.print_line(color_func(name + paren))



################################################################################
## Color helpers.
################################################################################

color_end = "\x1b[1;0m"
colors = dict(
    green="32",
    red="31",
    yellow="33",
    purple="35",
    cyan="36",
    blue="34"
)

def colorize(color, text, bold=False):
    bold = 1 if bold else 0
    return "\x1b[%s;%sm%s%s" % (bold, colors[color], text, color_end)

################################################################################
## Plugin itself.
################################################################################

class Spec(Plugin):
    """Generate specification from test class/method names.
    """
    score = 1100  # must be higher than Deprecated and Skip plugins scores

    def __init__(self, *args, **kwargs):
        super(Spec, self).__init__(*args, **kwargs)
        self._failures = []
        self._errors = []
        self.color = {}

    def options(self, parser, env=os.environ):
        Plugin.options(self, parser, env)
        parser.add_option('--no-spec-color', action='store_true',
                          dest='no_spec_color',
                          default=env.get('NOSE_NO_SPEC_COLOR'),
                          help="Don't show colors with --with-spec"
                          "[NOSE_NO_SPEC_COLOR]")
        parser.add_option('--spec-doctests', action='store_true',
                          dest='spec_doctests',
                          default=env.get('NOSE_SPEC_DOCTESTS'),
                          help="Include doctests in specifications "
                          "[NOSE_SPEC_DOCTESTS]")

    def configure(self, options, config):
        # Configure
        Plugin.configure(self, options, config)
        # Set options
        if options.enable_plugin_spec:
            options.verbosity = max(options.verbosity, 2)
        self.spec_doctests = options.spec_doctests
        # Color setup
        for label, color in {
            'error': 'red',
            'ok': 'green',
            'deprecated': 'yellow',
            'skipped': 'yellow',
            'failure': 'purple',
            'identifier': 'cyan',
            'file': 'blue',
        }.items():
            # No color: just print() really
            func = lambda text, bold=False: text
            if not options.no_spec_color:
                # Color: colorizes!
                func = partial(colorize, color)
            # Store in dict (slightly quicker/nicer than getattr)
            self.color[label] = func
            # Add attribute for easier hardcoded access
            setattr(self, label, func)

    def begin(self):
        self.current_context = None
        self.start_time = time.time()

    def setOutputStream(self, stream):
        self.stream = SpecOutputStream(stream, open(os.devnull, 'w'))
        return self.stream

    def beforeTest(self, test):
        context = testContext(test)
        if context != self.current_context:
            self._print_context(context)
            self.current_context = context

        self.stream.off()

    def addSuccess(self, test):
        self._print_spec('ok', test)

    def addFailure(self, test, err):
        self._print_spec('failure', test, 'FAILED')
        self._failures.append((test, err))

    def addError(self, test, err):
        def blurt(color, label):
            self._print_spec(color, test, label)

        klass = err[0]
        if issubclass(klass, nose.DeprecatedTest):
            blurt('deprecated', 'DEPRECATED')
        elif issubclass(klass, SkipTest):
            blurt('skipped', 'SKIPPED')
        else:
            self._errors.append((test, err))
            blurt('error', 'ERROR')

    def afterTest(self, test):
        self.stream.capture()

    def print_tracebacks(self, label, items):
        problem_color = {
            "ERROR": "error",
            "FAIL": "failure"
        }[label]
        for item in items:
            test, trace = item
            desc = test.shortDescription() or str(test)
            self.stream.writeln("=" * 70)
            self.stream.writeln("%s: %s" % (
                self.color[problem_color](label),
                self.identifier(desc, bold=True),
            ))
            self.stream.writeln("-" * 70)
            # format_exception() is...very odd re: how it breaks into lines.
            trace = "".join(traceback.format_exception(*trace)).split("\n")
            self.print_colorized_traceback(trace)

    def print_colorized_traceback(self, formatted_traceback, indent_level=0):
        indentation = "    " * indent_level
        for line in formatted_traceback:
            if line.startswith("  File"):
                m = re.match(r'  File "(.*)", line (\d*)(?:, in (.*))?$', line)
                if m:
                    filename, lineno, test = m.groups()
                    tb_lines = [
                        '  File "',
                        self.file(filename),
                        '", line ',
                        self.error(lineno),
                        ]
                    if test:
                        # this is missing for the first traceback in doctest
                        # failure report
                        tb_lines.extend([
                            ", in ",
                            self.identifier(test, bold=True)
                        ])
                    tb_lines.extend(["\n"])
                    self.stream.write(indentation)
                    self.stream.writelines(tb_lines)
                else:
                    print >>self.stream, indentation + line
            elif line.startswith("    "):
                print >>self.stream, self.identifier(indentation + line)
            elif line.startswith("Traceback (most recent call last)"):
                print >>self.stream, indentation + line
            else:
                print >>self.stream, self.error(indentation + line)

    def finalize(self, result):
        self.stream.on()
        print >>self.stream, ""
        self.print_tracebacks("ERROR", self._errors)
        self.print_tracebacks("FAIL", self._failures)
        self.print_summary(result)

    def print_summary(self, result):
        # Setup
        num_tests = result.testsRun
        success = result.wasSuccessful()
        # How many in how long
        print >>self.stream, "Ran %s test%s in %s" % (
            (self.ok if success else self.error)(num_tests),
            "s" if num_tests > 1 else "",
            self.format_seconds(time.time() - self.start_time)
        )
        # Did we fail, and if so, how badly?
        if success:
            print >>self.stream, self.ok("OK")
        else:
            types = (
                ('failures', 'failure'),
                ('errors', 'error'),
                ('skipped', 'skipped'),
            )
            pairs = []
            for label, color in types:
                num = len(getattr(result, label))
                text = str(num)
                if num:
                    text = self.color[color](text)
                pairs.append("%s=%s" % (label, text))
            print >>self.stream, "%s (%s)" % (
                self.failure("FAILED"),
                ", ".join(pairs)
            )
        print >>self.stream, ""

    def format_seconds(self, n_seconds):
        """Format a time in seconds."""
        func = self.ok
        if n_seconds >= 60:
            n_minutes, n_seconds = divmod(n_seconds, 60)
            return "%s minutes %s seconds" % (
                        func("%d" % n_minutes),
                        func("%.3f" % n_seconds))
        else:
            return "%s seconds" % (
                        func("%.3f" % n_seconds))

    def _print_context(self, context):
        if isinstance(context, doctest.DocTestCase) and not self.spec_doctests:
            return
        self.stream.print_context(context)

    def _print_spec(self, color, test, status=None):
        if isinstance(test.test, doctest.DocTestCase) and not self.spec_doctests:
            return
        self.stream.print_spec(self.color[color], test, status)
