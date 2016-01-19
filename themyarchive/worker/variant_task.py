# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime
import functools
import logging
import os
import random
import shutil
import subprocess

from themyarchive.app import app
from themyarchive.celery import celery
from themyarchive.db import db
from themyarchive.models import UrlVariant

logger = logging.getLogger(__name__)

__all__ = [b"variant_task"]


def variant_task(f, retry_exceptions=(Exception,)):
    @functools.wraps(f)
    def wrapper(self, variant_id):
        try:
            variant = db.session.query(UrlVariant).get(variant_id)
            url = variant.url

            archive_path = os.path.join(url.archive_path, str(variant_id))
            fs_archive_path = os.path.join(app.config["ARCHIVE_PATH"], archive_path)

            if os.path.exists(fs_archive_path):
                shutil.rmtree(fs_archive_path)
            os.makedirs(fs_archive_path)

            data = f(variant, fs_archive_path)

            for root, dirs, files in os.walk(fs_archive_path):
                for name in files:
                    path = os.path.join(root, name)
                    size = os.path.getsize(path)
                    if size > app.config["MAX_FILE_SIZE"]:
                        logger.warning("Removing too large file %r (size = %d)", path, size)
                        os.unlink(path)

            variant.data = dict(variant.data, **data)
            variant.data["archive_path"] = archive_path
            variant.is_ready = True
            variant.archived_at = datetime.now()
            variant.size = int(subprocess.check_output(["du", "-bs", fs_archive_path]).split("\t")[0])
            db.session.commit()

            return data
        except retry_exceptions as e:
            logger.error("Variant worker failed", exc_info=True)
            raise self.retry(exc=e, countdown=300 * int(random.uniform(2, 4) ** self.request.retries), max_retries=5)

    return celery.task(acks_late=True, bind=True)(wrapper)
