# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import timedelta
import os

SENTRY_DSN = os.getenv("SENTRY_DSN")

CELERY_BROKER_URL = "amqp://rabbitmq"
CELERYD_HIJACK_ROOT_LOGGER = False

SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://themyarchive:themyarchive@postgres/themyarchive"
SQLALCHEMY_ECHO = True

CHROME_PATH = "/themyarchive/docker/google-chrome/chrome.tar"

ARCHIVE_PATH = "/data"
ARCHIVE_URL = "/data"
ARCHIVE_URL_DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"

MAX_FILE_SIZE = 256e6
MIN_INTERVAL = timedelta(days=7)
RESOLUTIONS = [(1024, 768), (1440, 900), (1920, 1080)]
