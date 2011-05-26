# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='Spengler',
    version='0.1',
    description="Spengler Database Replication Validator",
    author='Tim Freund',
    author_email='tim@freunds.net',
    license = 'MIT License',
    url='http://github.com/timfreund/Spengler',
    install_requires=[
        'SQLAlchemy',
                ],
    packages=['spengler'],
    include_package_data=True,
    entry_points="""
    [console_scripts]
    spengler-daemon = spengler.cli:replication_check_daemon
    spengler-replication-check = spengler.cli:replication_check
    spengler-webserver = spengler.restful:run_server
    """,
)
