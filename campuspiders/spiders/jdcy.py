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

# 本站结构与 scc 极其类似, 只需修改对应元素的 CSS 或 XPath 表达式即可
SOURCE_ID_JDCY = 'jdcy'

# 元数据行形如: u'发布者：admin 发布时间：2012/12/3 阅读：次 【字体：  】'
METADATA_RE = re.compile(r'^发布者：(?P<publisher>.+?) 发布时间：(?P<ctime>\d+/\d+/\d+)')


class JDCYNewsSpider(CrawlSpider):
    name = 'jdcy'
    allowed_domains = ['jdcy.jiangnan.edu.cn', ]
    start_urls = [
            # http://jdcy.jiangnan.edu.cn/newsclass_通知公告_通知公告.html
            'http://jdcy.jiangnan.edu.cn/newsclass_%E9%80%9A%E7%9F%A5%E5%85%AC'
            '%E5%91%8A_%E9%80%9A%E7%9F%A5%E5%85%AC%E5%91%8A.html',
            ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/readnews_\d+.html']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_JDCY

        news['title'] = sel.css('.tit::text').extract()[0]

        news['content'] = normalize_content(sel.css('#fontzoom ::text').extract())

        metadata_line = ''.join(sel.xpath('/html/body/table[2]/tr/td/table/tr/td/table[2]/tr[2]/td[2]/text()').extract())
        metadata_match = METADATA_RE.match(metadata_line)

        news['author'] = ''
        news['publisher'] = metadata_match.group('publisher')
        news['ctime'] = strptime_helper(metadata_match.group('ctime'), '%Y/%m/%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
