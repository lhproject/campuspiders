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

SOURCE_ID_JW = 'jw'
NEWSINFO_METADATA_RE = re.compile(
        r'发布：(?P<publisher>[^ ]+)'
        r'\s+时间：\[(?P<ctime>\d+-\d+-\d+)\]'
        )
VIEWINFO_METADATA_RE = re.compile(
        r'添加时间：(?P<ctime>\d+-\d+-\d+)'
        r'\s+作者：\s*(?P<author>[^ ]+)'
        r'\s+来源：\s*(?P<source>[^ ]+)'
        r'\s+录入：\s*(?P<publisher>[^ ]+)'
        r'\s+阅读次数：\d+'
        )


class JWNewsSpider(CrawlSpider):
    name = 'jw'
    allowed_domains = ['jw.jiangnan.edu.cn', ]
    start_urls = ['http://jw.jiangnan.edu.cn/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/NewsInfo\.asp\?id=\d+']), 'parse_news_item_NewsInfo'),
            Rule(SgmlLinkExtractor(allow=[r'/ViewInfo\.asp\?id=\d+']), 'parse_news_item_ViewInfo'),
            ]

    def parse_news_item_NewsInfo(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_JW
        news['title'] = ''.join(sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr/td/strong/text()').extract())

        content_extracted = sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr[2]/td//text()').extract()
        news['content'] = normalize_content(content_extracted)

        metadata_str_extracted = sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr[3]/td/text()').extract()
        metadata_str = normalize_content(metadata_str_extracted).replace('\n', '')
        match = NEWSINFO_METADATA_RE.search(metadata_str)

        news['author'] = '未知'
        news['publisher'] = match.group('publisher')
        news['ctime'] = strptime_helper(match.group('ctime'), '%Y-%m-%d')

        return news

    def parse_news_item_ViewInfo(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_JW
        news['title'] = ''.join(sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/div/b/text()').extract())

        content_extracted = sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table[2]/tr/td//text()').extract()
        news['content'] = normalize_content(content_extracted)

        metadata_str_extracted = sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tr/td/div//text()').extract()
        metadata_str = normalize_content(metadata_str_extracted).replace('\n', '')
        match = VIEWINFO_METADATA_RE.search(metadata_str)

        news['author'] = match.group('author')
        news['publisher'] = match.group('publisher')
        news['ctime'] = strptime_helper(match.group('ctime'), '%Y-%m-%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
