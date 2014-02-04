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

SOURCE_ID_XINWEN = 'xinwen'


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
        news['title'] = sel.css('td.red::text').extract()[0]

        content_extracted = sel.xpath("//td[@class='list']/table/tr[5]/td//text()").extract()
        news['content'] = normalize_content(content_extracted)

        news['author'] = '未知'
        news['publisher'] = sel.css("a.username::text").extract()[0]

        ctime_str = sel.xpath("//td[@class='list']/table/tr/td[@align='center']/span[1]/text()").extract()[0]
        news['ctime'] = strptime_helper(ctime_str, '%Y-%m-%d %H:%M:%S')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
