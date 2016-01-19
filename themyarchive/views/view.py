# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from bs4 import BeautifulSoup
from datetime import datetime
from flask import abort, redirect, render_template, request, Response, url_for
import logging
import os
import re

from themyarchive.app import app
from themyarchive.db import db
from themyarchive.models import Url, UrlVariant
from themyarchive.utils import url_for_url

logger = logging.getLogger(__name__)

__all__ = []


@app.route("/view/<archived_at>/<variant>/<scheme>/<netloc>/")
def view_empty_path(archived_at, variant, scheme, netloc):
    return view(archived_at, variant, scheme, netloc, None)


@app.route("/view/<archived_at>/<variant>/<scheme>/<netloc>/<path:tail>")
def view(archived_at, variant, scheme, netloc, tail):
    prefix = "/view/%s/%s/%s/%s" % (archived_at, variant, scheme, netloc)
    path = request.environ["PATH_INFO"][len(prefix):]
    q = db.session.query(Url).\
            outerjoin(UrlVariant).\
            filter(
                Url.scheme == scheme.encode("ascii"),
                Url.netloc == netloc.encode("ascii"),
                Url.path == path if path.strip(b"/") != b"" else ((Url.path == b"/") | (Url.path == b"")),
                Url.query == request.environ["QUERY_STRING"],
            )
    if archived_at == "_":
        url = q.order_by(Url.archived_at.desc()).first()
    else:
        url = q.filter(Url.archived_at == datetime.strptime(archived_at, app.config["ARCHIVE_URL_DATETIME_FORMAT"])).first()

    if url is None:
        abort(404)

    variant_view = None
    if variant == "_":
        try:
            client_width = int(request.cookies["resolution"].split("x")[0])
        except (KeyError, ValueError):
            client_width = app.config["RESOLUTIONS"][0][0]

        try:
            variant = sorted(filter(lambda variant: (variant.variant == "google-chrome" and
                                                     variant.data["width"] < client_width + 20),
                                    url.ready_variants),
                             key=lambda variant: -variant.data["width"])[0]
            variant_view = "screenshot"
        except IndexError:
            try:
                variant = url.ready_variants[0]
            except IndexError:
                abort(503)
    else:
        m = re.match("(?P<view>[a-z]+)-(?P<width>[0-9]+)x(?P<height>[0-9]+)", variant)
        if m:
            for variant in url.variants:
                if variant.variant == "google-chrome":
                    if variant.data["width"] == int(m.group("width")) and\
                            variant.data["height"] == int(m.group("height")):
                        if variant.is_ready:
                            break
                        else:
                            abort(503)
            else:
                return redirect(url_for_url(url))
            variant_view = m.group("view")
        else:
            try:
                variant = filter(lambda v: v.variant == variant, url.variants)[0]
            except IndexError:
                return redirect(url_for_url(url))

            if not variant.is_ready:
                abort(503)

    header = render_template("view/header.html", url=url, variant=variant,
                             variants=([{"title": "Google Chrome %dx%d" % (v.data["width"],
                                                                           v.data["height"]),
                                         "is_current": variant == v,
                                         "views": ([{"title": "Screenshot",
                                                     "url": url_for_url(url, "screenshot-%dx%d" % (v.data["width"],
                                                                                                   v.data["height"])),
                                                     "is_current": v == variant and variant_view == "screenshot"},
                                                    {"title": "PDF",
                                                     "url": url_for_url(url, "pdf-%dx%d" % (v.data["width"],
                                                                                            v.data["height"])),
                                                     "is_current": v == variant and variant_view == "pdf"}] +
                                                   ([{"title": "HTML",
                                                      "url": url_for_url(url, "html-%dx%d" % (v.data["width"],
                                                                                              v.data["height"])),
                                                      "is_current": v == variant and variant_view == "html"}]
                                                    if "html" in v.data.get("features", ["html"]) else []))}
                                        for v in sorted(filter(lambda vv: vv.variant == "google-chrome",
                                                               url.ready_variants),
                                                        key=lambda vv: vv.data["width"])] +
                                       ([{"title": "wget HTML",
                                          "url": url_for_url(url, "wget"),
                                          "is_current": variant.variant == "wget"}]
                                        if any(v.variant == "wget" for v in url.ready_variants)
                                        else [])))

    if variant.variant == "google-chrome":
        if variant_view == "screenshot":
            src = "%s/%s/screenshot.png" % (app.config["ARCHIVE_URL"],
                                            variant.data["archive_path"])
            if os.path.getsize(os.path.join(app.config["ARCHIVE_PATH"],
                                            variant.data["archive_path"],
                                            "screenshot.png")) == 0:
                src = None
            html = render_template("view/screenshot.html", url=url, src=src)
            base = None
        elif variant_view == "pdf":
            return redirect("%s/%s/page.pdf" % (app.config["ARCHIVE_URL"],
                                                variant.data["archive_path"]))
        elif variant_view == "html":
            with open(os.path.join(app.config["ARCHIVE_PATH"], variant.data["archive_path"],
                                   "index.html")) as f:
                html = f.read()
                base = "%s/%s/" % (app.config["ARCHIVE_URL"],
                                   variant.data["archive_path"])
        else:
            return redirect(url_for_url(url))
    elif variant.variant == "wget":
        with open(os.path.join(app.config["ARCHIVE_PATH"], variant.data["archive_path"],
                               variant.data["relpath"])) as f:
            html = f.read()
            base = "%s/%s/%s" % (app.config["ARCHIVE_URL"],
                                 variant.data["archive_path"],
                                 variant.data["relpath"])
    else:
        return redirect(url_for_url(url))

    soup = BeautifulSoup(html)
    soup.head.insert(0, soup.new_tag("link", href=url_for("static", filename="header.css", _external=True),
                                     rel="stylesheet"))
    if base:
        soup.head.insert(0, soup.new_tag("base", href=base))
    soup.body.insert(0, list(BeautifulSoup(header).body)[0])
    return Response(soup.prettify())
