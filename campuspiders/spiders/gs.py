#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem

SOURCE_ID_GS = 'gs'

METADATA_RE = re.compile(r'^[\s　]+时间：(?P<ctime>\d+-\d+-\d+ \d+:\d+:\d+)')


class GSNewsSpider(CrawlSpider):
    name = 'gs'
    allowed_domains = ['gs.jiangnan.edu.cn', ]
    start_urls = ['http://gs.jiangnan.edu.cn/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/html/\d+/\d+.html']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_GS

        news['title'] = sel.css('.top_title_font::text').extract()[0]
        news['content'] = normalize_content(sel.xpath('//table[@width="85%"]/tr/td[@bgcolor="#FFFFFF"]//text()').extract())

        metadata_line = ''.join(sel.xpath('//td[@style="padding-left:6px; padding-right:6px"]/table[2]/tr/td[@height="30"]/text()').extract())
        metadata_match = METADATA_RE.match(metadata_line)

        news['author'] = '未知'
        news['publisher'] = ''
        news['ctime'] = strptime_helper(metadata_match.group('ctime'), '%Y-%m-%d %H:%M:%S')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
