# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from flask_restful import Api
import logging

from themyarchive.api.url import Url
from themyarchive.api.urls import RecentUrls, SearchUrls
from themyarchive.app import app

logger = logging.getLogger(__name__)

__all__ = [b"api"]

api = Api(app)
api.add_resource(Url, "/url")
api.add_resource(RecentUrls, "/urls/recent")
api.add_resource(SearchUrls, "/urls/search")
