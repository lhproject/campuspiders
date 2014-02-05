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

SOURCE_ID_SCC = 'scc'

METADATA_RE = re.compile(r'^发布者：(?P<publisher>.+?) 发布时间：(?P<ctime>\d+-\d+-\d+)')


class SCCNewsSpider(CrawlSpider):
    name = 'scc'
    allowed_domains = ['scc.jiangnan.edu.cn', ]
    start_urls = ['http://scc.jiangnan.edu.cn/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/readnews_\d+.html']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_SCC

        # ::text 选择器是 Scrapy 的非标准扩展, 参见:
        # http://stackoverflow.com/a/21182445/596531
        news['title'] = sel.css('.tit::text').extract()[0]

        news['content'] = normalize_content(sel.css('#fontzoom > div ::text').extract())

        metadata_line = ''.join(sel.xpath('/html/body/table/tr/td/table/tr/td/table[2]/tr[2]/td/div/text()').extract())
        metadata_match = METADATA_RE.match(metadata_line)

        news['author'] = '未知'
        news['publisher'] = metadata_match.group('publisher')
        news['ctime'] = strptime_helper(metadata_match.group('ctime'), '%Y-%m-%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
