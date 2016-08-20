# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from setuptools import find_packages, setup

logger = logging.getLogger(__name__)


setup(
    name="themyarchive",
    version="0.0.0",
    author="themylogin",
    packages=find_packages(exclude=[]),
    test_suite="nose.collector",
    dependency_links=[
        "https://github.com/themylogin/themyutils/archive/master.zip#egg=themyutils"
    ],
    install_requires=[
        "alembic",
        "beautifulsoup4",
        "celery==3.1.23",
        "docker-py",
        "Flask",
        "Flask-Bootstrap",
        "Flask-Restful",
        "Flask-Script",
        "Flask-SQLAlchemy",
        "psycopg2",
        "raven[flask]",
        "themyutils",
    ],
    setup_requires=[],
)
