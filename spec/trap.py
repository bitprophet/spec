"""
Test decorator for capturing stdout/stderr/both.

Based on original code from Fabric 1.x, specifically:

* fabric/tests/utils.py
* as of Git SHA 62abc4e17aab0124bf41f9c5f9c4bc86cc7d9412

Though modifications have been made since.
"""
import io
import sys

from functools import wraps


class CarbonCopy(io.BytesIO):
    """
    A io.BytesIO capable of multiplexing its writes to other buffer objects.
    """
    def __init__(self, buffer='', cc=None):
        """
        If ``cc`` is given and is a file-like object or an iterable of same,
        it/they will be written to whenever this io.BytesIO instance is written
        to.
        """
        io.BytesIO.__init__(self, buffer)
        if cc is None:
            cc = []
        elif hasattr(cc, 'write'):
            cc = [cc]
        self.cc = cc

    def write(self, s):
        io.BytesIO.write(self, s)
        for writer in self.cc:
            writer.write(s)


def trap(func):
    """
    Replaces sys.std(out|err) with ``io.BytesIO``s during the test, restored after.

    In addition, a new combined-streams output (another io.BytesIO) will appear
    at ``sys.stdall``. This io.BytesIO will resemble what a user sees at a
    terminal, i.e. both streams intermingled.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sys.stdall = io.BytesIO()
        my_stdout, sys.stdout = sys.stdout, CarbonCopy(cc=sys.stdall)
        my_stderr, sys.stderr = sys.stderr, CarbonCopy(cc=sys.stdall)
        try:
            ret = func(*args, **kwargs)
        finally:
            sys.stdout = my_stdout
            sys.stderr = my_stderr
            del sys.stdall
    return wrapper
