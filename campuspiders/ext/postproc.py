#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from scrapy import signals
from scrapy.exceptions import NotConfigured

# NOTE: 这一行导入会间接给微雨框架加载配置文件
from ..task import newsitem


class DBMaintenance(object):
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('DB_MAINTENANCE_ENABLED'):
            raise NotConfigured

        ext = cls()
        crawler.signals.connect(
                ext.spider_closed,
                signal=signals.spider_closed,
                )

        return ext

    def spider_closed(self, spider):
        spider.log('scheduling old index pruning for spider %s' % spider.name)
        newsitem.clean_index.delay()

        spider.log('scheduling short URL update for spider %s' % spider.name)
        newsitem.update_short_urls.delay()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
