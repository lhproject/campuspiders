#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import time

from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from luohua.utils.viewhelpers import jsonreply

from ...db.newsitem import NewsItemRecord

ONE_WEEK = 7 * 86400


@http
@jsonview
@only_methods(['GET', ])
def feed_one_week_v1_view(request):
    curtime = int(time.time())
    items = list(NewsItemRecord.get_recent_items(curtime - ONE_WEEK))

    return jsonreply(r=0, l=items)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
