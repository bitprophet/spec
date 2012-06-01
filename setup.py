from setuptools import setup, find_packages

setup(
    name='spec',
    version="0.9.5",
    description='Specification-style output for nose',
    author='Jeff Forcier',
    author_email='jeff@bitprophet.org',
    url='https://github.com/bitprophet/spec',
    license='MIT',
    packages=find_packages(),
    install_requires=['nose>=1.1,<1.2'],
    entry_points={
        'nose.plugins.0.10': [
            'spec = spec:SpecPlugin',
        ],
        'console_scripts': [
            'spec = spec:main'
        ],
    },
    use_2to3=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
    ]
)
