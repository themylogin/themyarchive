# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask import render_template
import logging

from themyarchive.app import app

logger = logging.getLogger(__name__)

__all__ = []


@app.route("/")
@app.route("/search")
def index():
    return render_template("index.html")
