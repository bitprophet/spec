from __future__ import unicode_literals

import re
from functools import partial

import six

from nose import SkipTest
# Gets us eq_, ok_, etc
# TODO: see what I or others are using here and make explicit, ugh
from nose.tools import *
from nose.tools import ok_ as upstream_ok_

from spec.plugin import SpecPlugin
from spec.cli import main
from spec.utils import InnerClassParser, hide
from spec.trap import trap


class Spec(six.with_metaclass(InnerClassParser, object)):
    """
    Parent class for spec classes wishing to use inner class contexts.
    """


# Simple helper
def skip():
    raise SkipTest


# Multiline string comparison helper ripped from Fabric 1.x
def eq_(result, expected, msg=None):
    """
    Shadow of the Nose builtin which presents easier to read multiline output.
    """
    params = {'expected': expected, 'result': result}
    aka = """

--------------------------------- aka -----------------------------------------

Expected:
%(expected)r

Got:
%(result)r
""" % params
    default_msg = """
Expected:
%(expected)s

Got:
%(result)s
""" % params
    if (
        (repr(result) != six.text_type(result)) or
        (repr(expected) != six.text_type(expected))
    ):
        default_msg += aka
    assertion_msg = msg or default_msg
    # This assert will bubble up to Nose's failure handling, which at some
    # point calls explicit str() - which will UnicodeDecodeError on any non
    # ASCII text.
    # To work around this, we make sure Unicode strings become bytestrings
    # beforehand, with explicit encode.
    if isinstance(assertion_msg, six.text_type):
        assertion_msg = assertion_msg.encode('utf-8')
    assert result == expected, assertion_msg


# Unicode-friendlier ok_
def ok_(assertion, msg=None):
    if msg is not None:
        # Same as in eq_ above re: need to correctly encode before nose calls
        # str()...
        if isinstance(msg, six.text_type):
            msg = msg.encode('utf-8')
    upstream_ok_(assertion, msg)


def _assert_contains(haystack, needle, invert, escape=False):
    """
    Test for existence of ``needle`` regex within ``haystack``.

    Say ``escape`` to escape the ``needle`` if you aren't really using the
    regex feature & have special characters in it.
    """
    myneedle = re.escape(needle) if escape else needle
    matched = re.search(myneedle, haystack, re.M)
    if (invert and matched) or (not invert and not matched):
        raise AssertionError("'%s' %sfound in '%s'" % (
            needle,
            "" if invert else "not ",
            haystack
        ))

assert_contains = partial(_assert_contains, invert=False)
assert_not_contains = partial(_assert_contains, invert=True)
