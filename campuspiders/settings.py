#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scrapy settings for campuspiders project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from __future__ import unicode_literals

BOT_NAME = 'campuspiders'

SPIDER_MODULES = ['campuspiders.spiders']
NEWSPIDER_MODULE = 'campuspiders.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'JNRain Campuspiders (+http://jnrain.com)'

ITEM_PIPELINES = {
        'campuspiders.pipelines.db.ItemStorePipeline': 900,
        }


# 一定要打开, 否则数据库索引和短链不会更新
EXTENSIONS = {
        'campuspiders.ext.postproc.DBMaintenance': 500,
        }

DB_MAINTENANCE_ENABLED = True


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
