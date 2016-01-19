# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import os
import sys
# When we run application with werkzeug reloader, it transfers `python -m appname` into `python .../appname/__main__.py`
# which adds app directory into sys.path which makes it impossible to create modules with common names like "celery"
# because then other packages using the same module name (e.g. themyutils.celery.beat) will fail to import because
# they will try to import from appname.celery first. This is why app directory should not be in sys.path
if os.path.dirname(__file__) in sys.path:
    sys.path.remove(os.path.dirname(__file__))

from celery.task.control import discard_all
import logging

from themyutils.sqlalchemy.sql import literal_query

from themyarchive import app
from themyarchive.manager import manager


@manager.command
def celery_purge():
    discard_all()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    manager.run()
