#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import time


def strptime_helper(s, fmt):
    return time.mktime(time.strptime(s, fmt))


def normalize_content(extracted):
    content = ''.join(extracted)
    content = content.replace('\r\n', '\n')
    content = content.replace('\xa0', ' ')
    return content


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
