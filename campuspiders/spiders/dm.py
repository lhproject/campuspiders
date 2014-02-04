#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import re
import time

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem
from ..linkextractors.dm import DMHomepageLinkExtractor

# XXX: 其实可以考虑直接实现个 API 在数媒学院官网里头, 反正是开源代码随便改...
# 不过实在是懒得动了那么就算了吧
SOURCE_ID_DM = 'dm'

# TODO: 直接解析 time 标签里的机器可读时间戳


class DMNewsSpider(CrawlSpider):
    name = SOURCE_ID_DM
    allowed_domains = ['dm.jiangnan.edu.cn', ]
    start_urls = ['http://dm.jiangnan.edu.cn/cn/', ]
    rules = [
            Rule(DMHomepageLinkExtractor(), 'parse_xue_article'),
            ]

    def parse_xue_article(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_DM
        news['title'] = sel.css('h1.title::text').extract()[0]

        content_elem = sel.css('.cms_article>:not(header)')
        news['content'] = normalize_content(content_elem.extract())

        #news['author'] = sel.css('span.author::text').extract()[0].strip()
        news['author'] = '未知'
        news['publisher'] = ''
        news['ctime'] = strptime_helper(sel.css('time.pubtime::text').extract()[0], '%Y.%m.%d %H:%M:%S')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
