# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from setuptools import find_packages, setup

logger = logging.getLogger(__name__)


setup(
    name="themyarchive",
    version="0.0.0",
    author="themylogin",
    author_email="themylogin@gmail.com",
    packages=find_packages(exclude=[]),
    scripts=[],
    test_suite="nose.collector",
    url="http://github.com/themylogin/themyarchive",
    description="",
    long_description="",
    install_requires=[
        "alembic",
        "celery",
        "Flask",
        "Flask-Bootstrap",
        "Flask-Restful",
        "Flask-Script",
        "Flask-SQLAlchemy",
        "sentry",
    ],
    setup_requires=[],
)
