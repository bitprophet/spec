from spec.plugin import SpecPlugin
from spec.cli import main
from spec.utils import InnerClassParser


class Spec(object):
    """
    Parent class for spec classes wishing to use inner class contexts.
    """
    __metaclass__ = InnerClassParser
