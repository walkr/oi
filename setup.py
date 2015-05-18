#!/usr/bin/env python

try:
    import setuptools
    from setuptools import setup
except ImportError:
    setuptools = None
    from distutils.core import setup


readme_file = 'README.md'
try:
    import pypandoc
    long_description = pypandoc.convert(readme_file, 'rst')
except (ImportError, OSError) as e:
    print('No pypandoc or pandoc: %s' % (e,))
    with open(readme_file) as fh:
        long_description = fh.read()

with open('./oi/version.py') as fh:
    for line in fh:
        if line.startswith('VERSION'):
            version = line.split('=')[1].strip().strip("'")

setup(
    name='oi',
    version=version,
    packages=['oi'],
    author='Tony Walker',
    author_email='walkr.walkr@gmail.com',
    url='https://github.com/walkr/oi',
    license='MIT',
    description='A library for writing long running processes with a cli interface',
    long_description=long_description,
    install_requires=[
        'nose',
        'nanoservice',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],

    entry_points={
        'console_scripts': [
            'oi = oi.script:main',
        ],
    },

)
