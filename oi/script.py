import os
import re
import sys
import random

from . import core


# =========================================================
# SKELETON FILES
# =========================================================

README = """
myprogram
=========
my program and its ctl
"""

Makefile = """
.PHONY: help test

help:
    @echo
    @echo "USAGE: make [target]"
    @echo
    @echo "TARGETS:"
    @echo
    @echo "  install        - install python package"
    @echo "  clean          - cleanup"
    @echo "  test           - run tests"
    @echo "  distribute     - upload to PyPI"
    @echo

install:
    @python setup.py install

test:
    @nosetests test

clean:
    @rm -rf build dist *.egg-info

distribute:
    @python setup.py register -r pypi && python setup.py sdist upload -r pypi
"""


setup = """

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
"""

myprogramd = """
import oi


def main():
    program = oi.Program('my program', 'ipc:///tmp/oi-random_string.sock')
    program.add_command('ping', lambda: 'pong')
    program.add_command('state', lambda: program.state)
    program.run()

if __name__ == '__main__':
    main()
"""

myprogramctl = """
import oi


def main():
    ctl = oi.CtlProgram('ctl program', 'ipc:///tmp/oi-random_string.sock')
    ctl.run()

if __name__ == '__main__':
    main()
"""


# =========================================================
# GENERATE SKELETON LOGIC
# =========================================================

def init_new_project(program):

    if os.listdir('.') != []:
        print('Directory not empty. Abort!')
        sys.exit(1)

    # ---

    name = os.path.basename(os.getcwd())

    src_dir = './{}'.format(name)
    os.mkdir(src_dir)

    # Add readme file
    with open('README.md', 'w') as fh:
        fh.write(README.replace('myprogram', name).lstrip())

    # Add setup script
    with open('setup.py', 'w') as fh:
        fh.write(setup.replace('myprogram', name).lstrip())

    # Add Makefile
    with open('Makefile', 'w') as fh:
        data = Makefile.replace('myprogram', name).lstrip()
        data = re.sub(r'    @', r'\t@', data)
        fh.write(data)

    # Add py files
    files = [
        ('myprogramd.py', myprogramd),
        ('myprogramctl.py', myprogramctl)]

    random_string = ''.join(random.sample([chr(i) for i in range(97, 123)], 10))

    for filename, var in files:
        filename = filename.replace('myprogram', name)
        with open(os.path.join(src_dir, filename), 'w') as fh:
            var = var.replace('myprogram', name).lstrip()
            var = var.replace('random_string', random_string)
            fh.write(var)

    # Add version file
    with open(os.path.join(src_dir, 'version.py'), 'w') as fh:
        fh.write("VERSION = '0.0.1\n'")

    # Add __init__ file
    with open(os.path.join(src_dir, '__init__.py'), 'w') as fh:
        pass


def main():
    program = core.CtlProgram(
        'init a new oi program in current empty directory', None)
    program.add_command('init', init_new_project)
    program.run(loop=False)


if __name__ == '__main__':
    main()
