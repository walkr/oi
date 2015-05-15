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

with open('./myprogram/version.py') as fh:
    for line in fh:
        if line.startswith('VERSION'):
            version = line.split('=')[1].strip().strip("'")

setup(
    name='myprogram',
    version=version,
    packages=['myprogram'],
    author='',
    author_email='',
    url='',
    # license='MIT',
    description='',
    long_description=long_description,
    install_requires=[
        'oi',
    ],
    classifiers=[
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],

    entry_points={
        'console_scripts': [
            'myprogramd = myprogram.myprogramd:main',
            'myprogramctl = myprogram.myprogramctl:main',
        ],
    },

)
