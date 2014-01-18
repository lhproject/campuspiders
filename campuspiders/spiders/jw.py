#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

import re
import time

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..items import JWNewsItem

NEWSINFO_METADATA_RE = re.compile(
        r'发布：(?P<publisher>[^ ]+)'
        r'\s+时间：\[(?P<y>\d+)-(?P<m>\d+)-(?P<d>\d+)\]'
        )
VIEWINFO_METADATA_RE = re.compile(
        r'添加时间：(?P<y>\d+)-(?P<m>\d+)-(?P<d>\d+)'
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
        news = JWNewsItem()

        news['url'] = response.url
        news['title'] = ''.join(sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr/td/strong/text()').extract())

        content = ''.join(sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr[2]/td//text()').extract())
        content = content.replace('\r\n', '\n')
        content = content.replace('\xa0', ' ')
        news['content'] = content

        metadata_str = ''.join(sel.xpath('/html/body/table[3]/tbody/tr/td/table[2]/tbody/tr[2]/td/table[4]/tr[3]/td/text()').extract())
        match = NEWSINFO_METADATA_RE.search(metadata_str)

        news['author'] = '未知'
        news['publisher'] = match.group('publisher')

        y, m, d = int(match.group('y')), int(match.group('m')), int(match.group('d'))
        news['ctime'] = time.mktime((y, m, d, 0, 0, 0, 0, 0, 0, ))

        return news

    def parse_news_item_ViewInfo(self, response):
        sel = Selector(response)
        news = JWNewsItem()

        news['url'] = response.url
        news['title'] = ''.join(sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td[2]/div/b/text()').extract())

        content = ''.join(sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table[2]/tr/td//text()').extract())
        content = content.replace('\r\n', '\n')
        content = content.replace('\xa0', ' ')
        news['content'] = content

        metadata_str = ''.join(sel.xpath('/html/body/table[4]/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tr/td/div//text()').extract())
        metadata_str = metadata_str.replace('\r\n', '\n')
        metadata_str = metadata_str.replace('\n', '')
        metadata_str = metadata_str.replace('\xa0', ' ')
        match = VIEWINFO_METADATA_RE.search(metadata_str)

        news['author'] = match.group('author')
        news['publisher'] = match.group('publisher')

        y, m, d = int(match.group('y')), int(match.group('m')), int(match.group('d'))
        news['ctime'] = time.mktime((y, m, d, 0, 0, 0, 0, 0, 0, ))

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
