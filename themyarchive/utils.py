# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask import url_for
import logging
import urllib

from themyarchive.app import app

logger = logging.getLogger(__name__)

__all__ = [b"url_for_url"]


def url_for_url(url, variant="_"):
    return (url_for("view", archived_at=url.archived_at.strftime(app.config["ARCHIVE_URL_DATETIME_FORMAT"]),
                    variant=variant, scheme=url.scheme, netloc=url.netloc, tail="", _external=True) +
            urllib.quote(url.path[1:]) +
            (b"?%s" % urllib.quote(url.query, b"/=") if url.query else b""))
