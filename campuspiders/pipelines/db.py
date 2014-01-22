#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from ..tasks.newsitem import add_item


class ItemStorePipeline(object):
    def process_item(self, item, spider):
        # Celery 即将抛弃 pickle 序列化格式, 那么我们不能直接传入一个类了
        add_item.delay(
                {
                    'source': item['source'],
                    'url': item['url'],
                    'title': item['title'],
                    'ctime': item['ctime'],
                    'author': item['author'],
                    'publisher': item['publisher'],
                    'content': item['content'],
                    },
                time.time(),
                )

        return item


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
