# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict


from themyarchive.db import db

__all__ = [b"Url", b"UrlVariant"]


class Url(db.Model):
    id                          = db.Column(db.Integer, primary_key=True)
    url                         = db.Column(db.String(8192), nullable=False)
    scheme                      = db.Column(db.Binary(8), nullable=False)
    netloc                      = db.Column(db.Binary(256), nullable=False)
    path                        = db.Column(db.Binary(8192), nullable=False)
    query                       = db.Column(db.Binary(8192), nullable=False)
    archived_at                 = db.Column(db.DateTime, nullable=False)
    archive_path                = db.Column(db.String(64), nullable=False)

    __table_args__              = (db.Index("ix_full_url", scheme, netloc, path, query),)

    @property
    def ready_variants(self):
        return filter(lambda variant: variant.is_ready, self.variants)


class UrlVariant(db.Model):
    id                          = db.Column(db.Integer, primary_key=True)
    url_id                      = db.Column(db.Integer, db.ForeignKey("url.id"))
    variant                     = db.Column(db.String(32), nullable=False)
    data                        = db.Column(MutableDict.as_mutable(JSON))
    is_ready                    = db.Column(db.Boolean, nullable=False, default=False)
    archived_at                 = db.Column(db.DateTime)
    size                        = db.Column(db.Integer)

    url                         = db.relationship("Url", backref="variants")
