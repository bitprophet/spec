"""
Test decorator for capturing stdout/stderr/both.

Based on original code from Fabric 1.x, specifically:

* fabric/tests/utils.py
* as of Git SHA 62abc4e17aab0124bf41f9c5f9c4bc86cc7d9412

Though modifications have been made since.
"""
import sys
from functools import wraps

import six
from six import BytesIO as IO


class CarbonCopy(IO):
    """
    An IO wrapper capable of multiplexing its writes to other buffer objects.
    """
    # NOTE: because StringIO.StringIO on Python 2 is an old-style class we
    # cannot use super() :(
    def __init__(self, buffer=b'', cc=None):
        """
        If ``cc`` is given and is a file-like object or an iterable of same,
        it/they will be written to whenever this instance is written to.
        """
        IO.__init__(self, buffer)
        if cc is None:
            cc = []
        elif hasattr(cc, 'write'):
            cc = [cc]
        self.cc = cc

    def write(self, s):
        # Ensure we always write bytes. This means that wrapped code calling
        # print(<a string object>) in Python 3 will still work. Sigh.
        if not isinstance(s, six.binary_type):
            s = s.encode('utf-8')
        # Write out to our capturing object & any CC's
        IO.write(self, s)
        for writer in self.cc:
            writer.write(s)

    # Dumb hack to deal with py3 expectations; real sys.std(out|err) in Py3
    # requires writing to a buffer attribute obj in some situations.
    @property
    def buffer(self):
        return self

    # Make sure we always hand back strings, even on Python 3
    def getvalue(self):
        ret = IO.getvalue(self)
        if six.PY3:
            ret = ret.decode('utf-8')
        return ret


def trap(func):
    """
    Replace sys.std(out|err) with a wrapper during execution, restored after.

    In addition, a new combined-streams output (another wrapper) will appear at
    ``sys.stdall``. This stream will resemble what a user sees at a terminal,
    i.e. both out/err streams intermingled.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Use another CarbonCopy even though we're not cc'ing; for our "write
        # bytes, return strings on py3" behavior. Meh.
        sys.stdall = CarbonCopy()
        my_stdout, sys.stdout = sys.stdout, CarbonCopy(cc=sys.stdall)
        my_stderr, sys.stderr = sys.stderr, CarbonCopy(cc=sys.stdall)
        try:
            ret = func(*args, **kwargs)
        finally:
            sys.stdout = my_stdout
            sys.stderr = my_stderr
            del sys.stdall
    return wrapper
