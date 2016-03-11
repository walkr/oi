#!/usr/bin/env python

import sys

try:
    import setuptools
    from setuptools import setup
except ImportError:
    setuptools = None
    from distutils.core import setup


is_py3 = sys.version_info.major == 3
readme_file = 'README.md'


def read_long_description(readme_file):
    """ Read package long description from README file """
    try:
        import pypandoc
    except (ImportError, OSError) as e:
        print('No pypandoc or pandoc: %s' % (e,))
        if is_py3:
            fh = open(readme_file, encoding='utf-8')
        else:
            fh = open(readme_file)
        long_description = fh.read()
        fh.close()
        return long_description
    else:
        return pypandoc.convert(readme_file, 'rst')


def read_version():
    """ Read package version """
    with open('./oi/version.py') as fh:
        for line in fh:
            if line.startswith('VERSION'):
                return line.split('=')[1].strip().strip("'")

setup(
    name='oi',
    version=read_version(),
    packages=['oi'],
    author='Tony Walker',
    author_email='walkr.walkr@gmail.com',
    url='https://github.com/walkr/oi',
    license='MIT',
    description='A library for writing long running processes '
                'with a cli interface',
    long_description=read_long_description(readme_file),
    install_requires=[
        'nose',
        'nanomsg',
        'nanoservice',
        'colorama',
    ],
    dependency_links=[
        'git+https://github.com/tonysimpson/nanomsg-python.git@master#egg=nanomsg',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'oi = oi.script:main',
        ],
    },
)
