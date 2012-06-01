from nose.util import isclass


def dont_show(obj):
    """
    Mark object as private.
    """
    obj._spec__is_private = True
    return obj

def is_public_class(name, value):
    return isclass(value) and not name.startswith('_')

def class_members(obj):
    return filter(lambda x: is_public_class(*x), vars(obj).iteritems())

def flag_inner_classes(obj):
    """
    Mutates any attributes on ``obj`` which are classes, with link to ``obj``.

    Recurses on those objects as well.
    """
    for tup in class_members(obj):
        tup[1]._parent = obj
        flag_inner_classes(tup[1])


class InnerClassParser(type):
    """
    Metaclass that tags inner classes with a link to the parent class.

    Allows test loading machinery to determine if a given test is part of an
    inner class or a top level one.
    """
    def __new__(cls, name, bases, attrs):
        # don't show setup nor teardown
        for x in ['setup', 'teardown']:
            if x in attrs:
                attrs[x] = dont_show(attrs[x])

        new_class = type.__new__(cls, name, bases, attrs)
        flag_inner_classes(new_class)
        return new_class
