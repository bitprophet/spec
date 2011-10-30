"""Unit tests for Spec plugin.
"""

import unittest
import nose
from nose.plugins import Plugin, PluginTester
from pinocchio.spec import Spec


def prepend_in_each_line(string, prefix='    '):
    return ''.join([prefix + s for s in string.splitlines(True)])

class SpecPluginTestCase(PluginTester, unittest.TestCase):
    activate  = '--with-spec'
    plugins   = [Spec()]

    def _get_suitepath(self):
        return 'tests/spec_test_cases/test_%s.py' % self.suitename
    suitepath = property(_get_suitepath)

    def assertContains(self, needle, haystack):
        assert needle in haystack,\
            "Failed to find:\n\n%s\ninside\n%s\n" % \
                (prepend_in_each_line(needle), prepend_in_each_line(haystack))

    def assertContainsInOutput(self, string):
        self.assertContains(string, str(self.output))

    def failIfContains(self, needle, haystack):
        assert needle not in haystack,\
            "Found:\n\n%s\ninside\n%s\n" % \
                (prepend_in_each_line(needle), prepend_in_each_line(haystack))

    def failIfContainsInOutput(self, string):
        self.failIfContains(string, str(self.output))

class TestPluginSpecWithFoobar(SpecPluginTestCase):
    suitename = 'foobar'
    expected_test_foobar_output = """Foobar
- can be automatically documented
- is a singleton
"""
    expected_test_bazbar_output = """Baz bar
- does this and that
"""
    def test_builds_specifications_for_test_classes(self):
        self.assertContainsInOutput(self.expected_test_foobar_output)

    def test_builds_specifications_for_unittest_test_cases(self):
        self.assertContainsInOutput(self.expected_test_bazbar_output)

class TestPluginSpecWithFoobaz(SpecPluginTestCase):
    suitename = 'foobaz'
    expected_test_foobaz_output = """Foobaz
- behaves such and such
- causes an error (ERROR)
- fails to satisfy this specification (FAILED)
- throws deprecated exception (DEPRECATED)
- throws skip test exception (SKIPPED)
"""
    def test_marks_failed_specifications_properly(self):
        self.assertContainsInOutput(self.expected_test_foobaz_output)

# Make sure DEPRECATED and SKIPPED are still present in the output when set
# of standard nose plugins is enabled.
class TestPluginSpecWithFoobazAndStandardPluginsEnabled(TestPluginSpecWithFoobaz):
    plugins = [Spec(), nose.plugins.skip.Skip(), nose.plugins.deprecated.Deprecated()]

class TestPluginSpecWithContainers(SpecPluginTestCase):
    suitename = 'containers'
    expected_test_containers_output = """Containers
- are marked as deprecated
- doesn't work with sets
"""
    def test_builds_specifications_for_test_modules(self):
        self.assertContainsInOutput(self.expected_test_containers_output)

class TestPluginSpecWithDocstringSpecNames(SpecPluginTestCase):
    suitename = 'docstring_spec_names'
    expected_test_docstring_spec_modules_names_output = """This module
- uses function to do this and that
"""
    expected_test_docstring_spec_class_names_output = """Yet another class
- has a nice descriptions inside test methods
- has a lot of methods
"""

    def test_names_specifications_after_docstrings_if_present(self):
        self.assertContainsInOutput(self.expected_test_docstring_spec_modules_names_output)
        self.assertContainsInOutput(self.expected_test_docstring_spec_class_names_output)

class TestPluginSpecWithTestGenerators(SpecPluginTestCase):
    suitename = 'test_generators'
    expected_test_test_generators_output = """Product of even numbers is even
- holds for 18, 8
- holds for 14, 12
- holds for 0, 4
- holds for 6, 2
- holds for 16, 10
"""
    def test_builds_specifications_for_test_generators(self):
        self.assertContainsInOutput(self.expected_test_test_generators_output)

class TestPluginSpecWithTestGeneratorsWithDescriptions(SpecPluginTestCase):
    suitename = 'test_generators_with_descriptions'
    expected_test_test_generators_with_descriptions_output = """Natural numbers truths
- for even numbers 18 and 8 their product is even as well
- for even numbers 14 and 12 their product is even as well
- for even numbers 0 and 4 their product is even as well
- for even numbers 6 and 2 their product is even as well
- for even numbers 16 and 10 their product is even as well
"""
    def test_builds_specifications_for_test_generators_using_description_attribute_if_present(self):
        self.assertContainsInOutput(self.expected_test_test_generators_with_descriptions_output)

class TestPluginSpecWithDoctests(SpecPluginTestCase):
    activate  = '--with-spec'
    args      = ['--with-doctest', '--doctest-tests', '--spec-doctests']
    plugins   = [Spec(), nose.plugins.doctests.Doctest()]

    suitename = 'doctests'
    expected_test_doctests_output = """test_doctests
- 2 + 3 returns 5
- None is nothing
- foobar throws "NameError: name 'foobar' is not defined"
"""
    def test_builds_specifications_for_doctests(self):
        self.assertContainsInOutput(self.expected_test_doctests_output)

class TestPluginSpecWithDoctestsButDisabled(SpecPluginTestCase):
    activate  = '--with-spec'
    args      = ['--with-doctest', '--doctest-tests'] # no --spec-doctests option
    plugins   = [Spec(), nose.plugins.doctests.Doctest()]
    suitename = 'doctests'

    def test_doesnt_build_specifications_for_doctests_when_spec_doctests_option_wasnt_set(self):
        self.failIfContainsInOutput("test_doctests")
        self.failIfContainsInOutput("2 + 3 returns 5")
