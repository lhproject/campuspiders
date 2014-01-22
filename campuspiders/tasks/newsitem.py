#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

__all__ = [
        'add_item',
        'clean_index',
        ]

from .celery import app
from ..db.newsitem import NewsItemRecord


@app.task(serializer='json')
def add_item(item, timestamp):
    db_item = NewsItemRecord()
    db_item['fetch_time'] = timestamp
    db_item['source'] = item['source']
    db_item['url'] = item['url']
    db_item['ctime'] = item['ctime']
    db_item['title'] = item['title']
    db_item['content'] = item['content']
    db_item.save()

    return True


@app.task(serializer='json')
def clean_index():
    NewsItemRecord.purge_old_index()

    return True


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
