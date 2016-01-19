# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
from flask.ext.sqlalchemy import SQLAlchemy

from themyarchive.app import app

logger = logging.getLogger(__name__)

__all__ = [b"db"]

db = SQLAlchemy(app)
