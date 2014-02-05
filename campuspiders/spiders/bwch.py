#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem

# 注: 此站虽然也使用通元 CMS 构建, 但页面结构与 nic 和 hqc 略有不同,
# 因此没有采取提取公共类 (如 TongyuanCMSNewsSpider) 的方式制作.
SOURCE_ID_BWCh = 'bwch'


class BWChNewsSpider(CrawlSpider):
    name = 'bwch'
    allowed_domains = ['bwch.jiangnan.edu.cn', ]
    start_urls = ['http://bwch.jiangnan.edu.cn/gzdt/tzgg/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/gzdt/tzgg/\d+.shtml']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_BWCh

        news['title'] = sel.css('.biaoti::text').extract()[0]
        news['content'] = normalize_content(sel.css('#contentText ::text').extract())

        # 关于良心的话就不多说了
        news['author'] = '未知'
        news['publisher'] = normalize_content(sel.css('.xiangn > span:nth-child(3)::text').extract()[0]).strip()

        ctime_str = sel.css('.xiangn > span:nth-child(1)::text').extract()[0]
        news['ctime'] = strptime_helper(ctime_str, '%Y-%m-%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
