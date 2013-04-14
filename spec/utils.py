import six

from nose.util import isclass


def hide(obj):
    """
    Mark object as private.
    """
    obj._spec__is_private = True
    return obj

def is_public_class(name, value):
    return isclass(value) and not name.startswith('_')

def class_members(obj):
    return [x for x in six.iteritems(vars(obj)) if is_public_class(*x)]

def my_getattr(self, name):
    if not self._parent_inst:
        parent = self._parent()
        parent.setup()
        self._parent_inst = parent
    return getattr(self._parent_inst, name)

def flag_inner_classes(obj):
    """
    Mutates any attributes on ``obj`` which are classes, with link to ``obj``.

    Adds a convenience accessor which instantiates ``obj`` and then calls its
    ``setup`` method.

    Recurses on those objects as well.
    """
    for tup in class_members(obj):
        tup[1]._parent = obj
        tup[1]._parent_inst = None
        tup[1].__getattr__ = my_getattr
        flag_inner_classes(tup[1])

def autohide(obj):
    """
    Automatically hide setup() and teardown() methods, recursively.
    """
    # Members on obj
    for name, item in six.iteritems(vars(obj)):
        if callable(item) and name in ('setup', 'teardown'):
            item = hide(item)
    # Recurse into class members
    for name, subclass in class_members(obj):
        autohide(subclass)


class InnerClassParser(type):
    """
    Metaclass that tags inner classes with a link to the parent class.

    Allows test loading machinery to determine if a given test is part of an
    inner class or a top level one.
    """
    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)
        flag_inner_classes(new_class)
        autohide(new_class)
        return new_class
