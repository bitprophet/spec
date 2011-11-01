import inspect
import sys

import nose

#
# Custom selection logic
#


def private(obj):
    return obj.__name__.startswith('_')


class SpecSelector(nose.selector.Selector):
    def wantDirectory(self, dirname):
        # Given a sane root such as tests/, we want everything.
        # Some other mechanism already allows for hidden directories using a _
        # prefix, e.g. _support.
        return True

    def wantFile(self, filename):
        # Same as with directories -- anything unhidden goes.
        return True

    def wantModule(self, module):
        # You guessed it -- if it's being picked up as a module, we want it.
        # However, also store it so we can tell apart "native" class/func
        # objects from ones imported *into* test modules.
        if not hasattr(self, '_valid_modules'):
            self._valid_modules = []
        self._valid_modules.append(module)
        return True

    def wantFunction(self, function):
        # Only use locally-defined functions
        local = inspect.getmodule(function) in self._valid_modules
        # And not ones which are conventionally private
        good = local and not private(function)
        return good

    def wantClass(self, class_):
        # As with modules, track the valid ones for use in method testing.
        # Valid meaning defined locally in a valid module, and not private.
        if not hasattr(self, '_valid_classes'):
            self._valid_classes = []
        valid = inspect.getmodule(class_) in self._valid_modules
        good = valid and not private(class_)
        if good:
            self._valid_classes.append(class_)
        return good

    def wantMethod(self, method):
        # As with functions, we want only items defined on also-valid
        # containers (classes), and only ones not conventionally private.
        valid_class = method.im_class in self._valid_classes
        # And ones only defined local to the class in question, not inherited
        # from its parents. Also handle oddball 'type' cases.
        if method.im_class is type:
            return False
        # Handle 'contributed' methods not defined on class itself
        if not hasattr(method.im_class, method.__name__):
            return False
        candidates = list(reversed(method.im_class.mro()))[:-1]
        for candidate in candidates:
            if hasattr(candidate, method.__name__):
                return False
        return valid_class and not private(method)


# Silly plugin for loading selector
class CustomSelector(nose.plugins.Plugin):
    enabled = True

    def configure(self, options, conf):
        pass

    def prepareTestLoader(self, loader):
        loader.selector = SpecSelector(loader.config)
        pass


# Nose invocation
def main():
    args = [
        # Don't capture stdout
        '--nocapture',
        # Use the spec plugin
        '--with-spec',
        # Enable useful asserts
        '--detailed-errors',
        # Only look in tests/
        '--where=tests',
    ]
    nose.core.run(
        argv=['nosetests'] + args + sys.argv[1:],
        addplugins=[CustomSelector()],
    )
