from setuptools import setup, find_packages

setup(
    name='spec',
    version="0.1",
    description = 'Specification-style output for nose',
    author = 'Jeff Forcier',
    author_email = 'jeff@bitprophet.org',
    license = 'MIT',
    packages = find_packages(),
    entry_points = {
        'nose.plugins.0.10': [
            'spec = spec:Spec',
        ]},
)
