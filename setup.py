from setuptools import setup, find_packages

# Version info -- read without importing
_locals = {}
with open('spec/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']

setup(
    name='spec',
    version=version,
    description='Specification-style output for nose',
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    url='https://github.com/bitprophet/spec',
    license='MIT',
    packages=find_packages(),
    install_requires=['nose>=1.3', 'six'],
    dependency_links=[
        'https://github.com/nose-devs/nose/tarball/c0f777e488337dc7dde933453799986c46b37deb#egg=nose-1.3.0',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'spec = spec:SpecPlugin',
            'specselector = spec.cli:CustomSelector',
        ],
        'console_scripts': [
            'spec = spec:main'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Testing'
    ]
)
