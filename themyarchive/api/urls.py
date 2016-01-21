# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask_restful import Resource, reqparse
import logging
from sqlalchemy.orm import joinedload

from themyarchive.db import db
from themyarchive.models import Url
from themyarchive.utils import url_for_url

logger = logging.getLogger(__name__)

__all__ = [b"RecentUrls", b"SearchUrls"]


class UrlsResource(Resource):
    def _serve_urls(self, urls):
        return [{"url": url.url,
                 "view": url_for_url(url),
                 "archived_at": url.archived_at.isoformat(),
                 "variants": [{"variant": variant.variant,
                               "data": variant.data,
                               "is_ready": variant.is_ready}
                              for variant in url.variants]}
                 for url in urls]


class RecentUrls(UrlsResource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", help="Number of URLs to return", type=int, default=50)
        args = parser.parse_args()

        return self._serve_urls(db.session.query(Url).\
                        options(joinedload(Url.variants)).\
                        order_by(Url.id.desc()).\
                        limit(args.limit))


class SearchUrls(UrlsResource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("q", help="Number of URLs to return", type=str, required=True)
        args = parser.parse_args()

        return self._serve_urls(db.session.query(Url).\
                        options(joinedload(Url.variants)).\
                        filter(Url.url.contains(args.q)).\
                        order_by(Url.id.desc()))
