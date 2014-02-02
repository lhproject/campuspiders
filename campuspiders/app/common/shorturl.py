#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import time

from weiyu.shortcuts import http, view, renderable
from weiyu.utils.decorators import only_methods

from ...db.newsitem import NewsItemRecord


@http
@renderable('dummy')
@view
@only_methods(['GET', ])
def shorturl_goto_view(request, short_url):
    short_url_exists, long_url = NewsItemRecord.query_short_url(short_url)

    if short_url_exists:
        return 302, {}, {'location': long_url, }

    return 404, {}, {'mimetype': 'text/plain', }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
