#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem

SOURCE_ID_NIC = 'nic'


class NICNewsSpider(CrawlSpider):
    name = 'nic'
    allowed_domains = ['nic.jiangnan.edu.cn', ]
    start_urls = ['http://nic.jiangnan.edu.cn/xwdt/tzgg/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/xwdt/tzgg/\d+.shtml']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_NIC

        news['title'] = sel.css('.newstitle > h1::text').extract()[0]
        news['content'] = normalize_content(sel.css('#contentText ::text').extract())

        # 文章元数据居然人性地放在了不同的元素里, 不用上正则, 简直良心
        news['author'] = '未知'
        # 这里可能会出现 u'\xa0', 需要标准化掉
        news['publisher'] = normalize_content(sel.css('.newstitle > span > b:nth-child(3)::text').extract()[0])

        ctime_str = sel.css('.newstitle > span > b:nth-child(1)::text').extract()[0]
        news['ctime'] = strptime_helper(ctime_str, '%Y/%m/%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
