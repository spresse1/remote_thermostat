#! /usr/bin/env python

from setuptools import setup

# Begin from tox docs
# http://tox.readthedocs.org/en/latest/example/basic.html
# Modified to work from a tox subdir
from setuptools.command.test import test as TestCommand
from os import chdir
import sys

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        # Change to the dir containing tox bits
        chdir("..")
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)
# end from tox docs

setup(
    name="Remote Thermostat Daemon",
    version = "0.1",
    entry_points = {
        'console_scripts': [
            'remote_thermo_daemon = thermo_daemon:main'
        ]
    },
    install_requires = [
        "Adafruit-BBIO",
        "radiotherm",
        "requests",
    ],
    tests_require=['tox'],
    cmdclass = {'test': Tox},
)
