# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask.ext.bootstrap import Bootstrap
from raven.contrib.flask import Sentry
import sys
from werkzeug.exceptions import HTTPException

from themyarchive.app import app
from themyarchive.celery import celery
from themyarchive.db import db
from themyarchive.models import *

import themyarchive.api
import themyarchive.views
import themyarchive.worker

Bootstrap(app)

if app.config["SENTRY_DSN"]:
    runner = sys.argv[0].split("/")[-1]
    if runner in ["celery", "gunicorn", "uwsgi"]:
        app.config["RAVEN_IGNORE_EXCEPTIONS"] = [HTTPException]
        sentry = Sentry(app, wrap_wsgi=runner != "gunicorn")
