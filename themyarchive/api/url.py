# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime
from flask import abort
from flask_restful import Resource, reqparse
import hashlib
import logging
import re
import urlparse
import urllib

from themyarchive.app import app
from themyarchive.db import db
from themyarchive.models import Url as UrlModel, UrlVariant
from themyarchive.utils import url_for_url
from themyarchive.worker.google_chrome import google_chrome
from themyarchive.worker.wget import wget

logger = logging.getLogger(__name__)

__all__ = [b"Url"]


class Url(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("url", help="URL to archive", type=unicode, required=True)
        args = parser.parse_args()

        url = db.session.query(UrlModel).\
                filter(
                    UrlModel.url == args["url"],
                    UrlModel.archived_at >= datetime.now() - app.config["MIN_INTERVAL"]
                ).\
                order_by(UrlModel.archived_at.desc()).\
                first()
        if url:
            return {"view": url_for_url(url)}

        o = urlparse.urlsplit(urllib.unquote(args["url"].encode("utf-8")))
        if o.scheme == "" or o.netloc == "":
            abort(400)

        url = UrlModel()
        url.url = args["url"]

        url.scheme = o.scheme
        url.netloc = o.netloc
        url.path = o.path
        url.query = o.query

        url.archived_at = datetime.utcnow().replace(microsecond=0)

        hash = hashlib.sha1(url.url.encode("utf-8") + url.archived_at.isoformat()).hexdigest()
        url.archive_path = "/".join(filter(None, re.split("(.{2})", hash))[:3] + [hash])

        db.session.add(url)

        for width, height in app.config["RESOLUTIONS"]:
            self._create_variant(url, "google-chrome", {"width": width, "height": height}, google_chrome)

        self._create_variant(url, "wget", {}, wget)

        return {"view": url_for_url(url)}

    def _create_variant(self, url, v, data, task):
        variant = UrlVariant()
        variant.url = url
        variant.variant = v
        variant.data = data
        db.session.commit()
        task.delay(variant.id)
