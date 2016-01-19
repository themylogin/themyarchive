# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask import Flask
import logging

import themyarchive.config

logger = logging.getLogger(__name__)

__all__ = [b"app"]

app = Flask("themyarchive")
app.config.from_object(themyarchive.config)
