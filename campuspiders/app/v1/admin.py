#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from luohua.app.session.decorators import require_cap
from luohua.utils.viewhelpers import jsonreply


@http
@jsonview
@require_cap('campuspiders.admin')
@only_methods(['GET', ])
def admin_ping_v1_view(request):
    return jsonreply(r=0, s='pong')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
