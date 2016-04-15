#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup

setup(name='Distutils',
	version='1.0',
	description='Utilities to proxy APIs without CORS headers',
	author='Steven Presser',
	author_email='corsproxy@pressers.name',
	url='https://github.com/spresse1/CORSProxy',
	packages=['CORSProxy'],
	requires=[
		"WSGIProxy",
	],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Environment :: No Input/Output (Daemon)",
		"Environment :: Web Environment",
		"Framework :: Paste",
		"Intended Audience :: Developers",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python :: 2.7",
		"Topic :: Internet :: Proxy Servers",
		"Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
		"Topic :: Software Development :: Libraries",
	],
	setup_requires=['pytest-runner', ],
	tests_require=[
		'pytest',
		"coverage",
		"mock",
		"tox",
		"WSGIProxy",
	],
)
