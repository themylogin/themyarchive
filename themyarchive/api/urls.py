# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask_restful import Resource, reqparse
import logging
from sqlalchemy.orm import joinedload

from themyarchive.db import db
from themyarchive.models import Url
from themyarchive.utils import url_for_url

logger = logging.getLogger(__name__)

__all__ = [b"RecentUrls"]


class RecentUrls(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("limit", help="Number of URLs to return", type=int, default=50)
        args = parser.parse_args()

        return [{"url": url.url,
                 "view": url_for_url(url),
                 "archived_at": url.archived_at.isoformat(),
                 "variants": [{"variant": variant.variant,
                               "data": variant.data,
                               "is_ready": variant.is_ready}
                              for variant in url.variants]}
                for url in db.session.query(Url).\
                        options(joinedload(Url.variants)).\
                        order_by(Url.id.desc()).\
                        limit(args.limit)]
