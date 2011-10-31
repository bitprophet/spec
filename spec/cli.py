import sys

import nose


def main():
    args = [
        # Don't capture stdout
        '--nocapture',
        # Use the spec plugin
        '--with-spec',
        # Enable useful asserts
        '--detailed-errors',
    ]
    nose.core.run(argv=['nosetests'] + args + sys.argv[1:])
