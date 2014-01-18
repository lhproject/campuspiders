#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import re
import time

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..items import NewsItem

SOURCE_ID_XINWEN = 'xinwen'

CTIME_RE = re.compile('(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)')


def make_ctime_from_str(s):
    match = CTIME_RE.search(s)
    if match is None:
        raise ValueError('unexpected ctime string format')

    y, m, d, h, i, s = [int(i) for i in match.groups()]
    return time.mktime((y, m, d, h, i, s, 0, 0, 0, ))


class XinwenNewsSpider(CrawlSpider):
    name = 'xinwen'
    allowed_domains = ['xinwen.jiangnan.edu.cn', ]
    start_urls = ['http://xinwen.jiangnan.edu.cn/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/[A-Za-z]+/\d+/\d+/\d+.html']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_XINWEN
        news['title'] = sel.xpath("//td[@class='red']/text()").extract()[0]

        content = ''.join(sel.xpath("//td[@class='list']/table/tr[5]/td//text()").extract())
        content = content.replace('\r\n', '\n')
        content = content.replace('\xa0', ' ')
        news['content'] = content

        news['author'] = '未知'
        news['publisher'] = sel.xpath("//a[@class='username']/text()").extract()[0]
        news['ctime'] = make_ctime_from_str(sel.xpath("//td[@class='list']/table/tr/td[@align='center']/span[1]/text()").extract()[0])

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
