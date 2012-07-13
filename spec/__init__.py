from nose import SkipTest
from nose.tools import *

from spec.plugin import SpecPlugin
from spec.cli import main
from spec.utils import InnerClassParser, hide
from spec.trap import trap


class Spec(object):
    """
    Parent class for spec classes wishing to use inner class contexts.
    """
    __metaclass__ = InnerClassParser


# Simple helper
def skip():
    raise SkipTest
