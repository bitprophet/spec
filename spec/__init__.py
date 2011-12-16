from spec.plugin import Spec
from spec.cli import main
from spec.utils import InnerClassParser


class SpecSuperclass(object):
    __metaclass__ = InnerClassParser
