import inspect
import sys
import os

import nose
import six

from spec.utils import class_members


#
# Custom selection logic
#


def private(obj):
    return obj.__name__.startswith('_') or \
           getattr(obj, '_spec__is_private', False)


class SpecSelector(nose.selector.Selector):
    def __init__(self, *args, **kwargs):
        super(SpecSelector, self).__init__(*args, **kwargs)
        self._valid_modules = []
        # Handle --tests=
        self._valid_named_modules = map(os.path.abspath, self.config.testNames)
        self._valid_classes = []

    def wantDirectory(self, dirname):
        # Given a sane root such as tests/, we want everything.
        # Some other mechanism already allows for hidden directories using a _
        # prefix, e.g. _support.
        return True

    def wantFile(self, filename):
        # Same as with directories -- anything unhidden goes.
        # Also skip .pyc files
        is_pyc = os.path.splitext(filename)[1] == '.pyc'
        is_hidden = os.path.basename(filename).startswith('_')
        return not (is_pyc or is_hidden)

    def wantModule(self, module):
        # You guessed it -- if it's being picked up as a module, we want it.
        # However, also store it so we can tell apart "native" class/func
        # objects from ones imported *into* test modules.
        self._valid_modules.append(module)
        return True

    def wantFunction(self, function):
        # Only use locally-defined functions
        local = inspect.getmodule(function) in self._valid_modules
        # And not ones which are conventionally private
        good = local and not private(function)
        return good

    def registerGoodClass(self, class_):
        """
        Internal bookkeeping to handle nested classes
        """
        # Class itself added to "good" list
        self._valid_classes.append(class_)
        # Recurse into any inner classes
        for name, cls in class_members(class_):
            if self.isValidClass(cls):
                self.registerGoodClass(cls)

    def isValidClass(self, class_):
        """
        Needs to be its own method so it can be called from both wantClass and
        registerGoodClass.
        """
        module = inspect.getmodule(class_)
        valid = (
            module in self._valid_modules
            or module.__file__ in self._valid_named_modules
        )
        return valid and not private(class_)

    def wantClass(self, class_):
        # As with modules, track the valid ones for use in method testing.
        # Valid meaning defined locally in a valid module, and not private.
        good = self.isValidClass(class_)
        if good:
            self.registerGoodClass(class_)
        return good

    def wantMethod(self, method):
        if six.PY3:
            cls = method.__self__.__class__
        else:
            # Short-circuit on odd results
            if not hasattr(method, 'im_class'):
                return False
            cls = method.im_class

        # As with functions, we want only items defined on also-valid
        # containers (classes), and only ones not conventionally private.
        valid_class = cls in self._valid_classes
        # And ones only defined local to the class in question, not inherited
        # from its parents. Also handle oddball 'type' cases.
        if cls is type:
            return False
        # Handle 'contributed' methods not defined on class itself
        if not hasattr(cls, method.__name__):
            return False
        # Only test for mro on new-style classes. (inner old-style classes lack
        # it.)
        if hasattr(cls, 'mro') and callable(cls.mro):
            candidates = list(reversed(cls.mro()))[:-1]
            for candidate in candidates:
                if hasattr(candidate, method.__name__):
                    return False
        ok = valid_class and not private(method)
        return ok


# Plugin for loading selector & implementing some custom hooks too
# (such as appending more test cases from gathered classes)
class CustomSelector(nose.plugins.Plugin):
    name = "specselector"

    def configure(self, options, conf):
        nose.plugins.Plugin.configure(self, options, conf)

    def prepareTestLoader(self, loader):
        loader.selector = SpecSelector(loader.config)
        self.loader = loader

    def loadTestsFromTestClass(self, cls):
        """
        Manually examine test class for inner classes.
        """
        results = []
        for name, subclass in class_members(cls):
            results.extend(self.loader.loadTestsFromTestClass(subclass))
        return results


def args_contains(options):
    for opt in options:
        for arg in sys.argv[1:]:
            if arg.startswith(opt):
                return True
    return False


# Nose invocation
def main():
    defaults = [
        # Don't capture stdout
        '--nocapture',
        # Use the spec plugin
        '--with-specplugin', '--with-specselector',
        # Enable useful asserts
        '--detailed-errors',
    ]
    # Set up default test location ('tests/') and custom selector,
    # only if user isn't giving us specific options of their own.
    # FIXME: see if there's a way to do it post-optparse, this is brittle.
    good = not args_contains("--match -m -i --include -e --exclude".split())
    plugins = []
    if good and os.path.isdir('tests'):
        plugins = [CustomSelector()]
        if not args_contains(['--tests', '-w', '--where']):
            defaults.append("--where=tests")
    nose.core.main(
        argv=['nosetests'] + defaults + sys.argv[1:],
        addplugins=plugins
    )
