"""
Stopwatch plugin for 'nose'.


"""
import sys
err = sys.stderr

from cPickle import dump, load
import time
import logging
import os
from nose.plugins.base import Plugin

log = logging.getLogger(__name__)

class Stopwatch(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self.dontrun = {}
        self.times = {}
        
    def add_options(self, parser, env=os.environ):
        Plugin.add_options(self, parser, env)
        parser.add_option("--faster-than",
                          action="store",
                          type="float",
                          dest="faster_than",
                          default=None,
                          help="Run only tests that are faster than FASTER_THAN seconds.")
        parser.add_option("--stopwatch-file",
                          action="store",
                          dest="stopwatch_file",
                          default=".nose-stopwatch-times",
                          help="Store test timing results in this file.")

    def configure(self, options, config):
        ### configure logging
        logger = logging.getLogger(__name__)
        logger.propagate = 0

        handler = logging.StreamHandler(err)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        
        Plugin.configure(self, options, config)

        ### configure stopwatch stuff: file containing times, and
        ### time cutoff.

        self.stopwatch_file = os.path.abspath(options.stopwatch_file)
        self.faster_than = options.faster_than

        log.info('stopwatch module: using "%s" for stopwatch times' % \
                 (self.stopwatch_file,))
        log.info('selecting tests that run faster than %s seconds' % \
                 (self.faster_than,))

    def begin(self):
        """
        Run before any of the tests run.  Loads the stopwatch file, and
        calculates which tests should NOT be run.
        """
        try:
            self.times = load(open(self.stopwatch_file))
        except (IOError, EOFError):
            self.times = {}

        # figure out which tests should NOT be run.

        faster_than = self.faster_than
        if faster_than is not None:
            for (k, v) in self.times.items():
                if v > faster_than:
                    self.dontrun[k] = 1

    def finalize(self, result):
        """
        Save the recorded times, OR dump them into /tmp if the file
        open fails.
        """
        try:
            fp = open(self.stopwatch_file, 'w')
        except (IOError, OSError):
            t = int(time.time())
            filename = '/tmp/nose-stopwatch-%s.pickle' % (t,)
            fp = open(filename, 'w')
            log.warning('WARNING: stopwatch cannot write to "%s"' % (self.stopwatch_file))
            log.warning('WARNING: stopwatch is using "%s" to save times' % (filename,))
            
        dump(self.times, fp)
        fp.close()

    def wantMethod(self, method):
        """
        Do we want to run this method?  See _should_run.
        """
        fullname = '%s.%s.%s' % (method.__module__,
                                 method.im_class.__name__,
                                 method.__name__)

        return self._should_run(fullname)

    def wantFunction(self, func):
        """
        Do we want to run this function?  See _should_run.
        """
        fullname = '%s.%s' % (func.__module__,
                              func.__name__)

        return self._should_run(fullname)

    ### note, no wantClass, because classes only *contain* tests, but
    ### aren't tests themselves.

    def _should_run(self, name):
        """
        If we have this test listed as "don't run" because of explicit
        time constraints, don't run it.  Otherwise, indicate no preference.
        """
        if self.dontrun.has_key(name):
            return False

        return None
        
    def startTest(self, test):
        """
        startTest: start timing.
        """
        self._started = time.time()

    def stopTest(self, test):
        """
        stopTest: stop timing, canonicalize the test name, and save
        the run time.
        """
        runtime = time.time() - self._started

        # CTB: HACK!
        testname = str(test)
        if ' ' in testname:
            testname = testname.split(' ')[1]
            
        self.times[testname] = runtime
