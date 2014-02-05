#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem

# 注: 此站和 nic 几乎完全一致, 今后维护可以考虑提取公共处理部分
SOURCE_ID_HQC = 'hqc'


class HQCNewsSpider(CrawlSpider):
    name = 'hqc'
    allowed_domains = ['hqc.jiangnan.edu.cn', ]
    start_urls = ['http://hqc.jiangnan.edu.cn/xwdt/tzgg/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/xwdt/tzgg/\d+.shtml']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_HQC

        news['title'] = sel.css('.se_n_ir_titt::text').extract()[0]
        news['content'] = normalize_content(sel.css('#contentText ::text').extract())

        # 同样良心
        news['author'] = '未知'
        # 这里可能会出现 u'\xa0', 需要标准化掉
        news['publisher'] = normalize_content(sel.css('.newstitle > span > b:nth-child(3)::text').extract()[0]).strip()

        ctime_str = sel.css('.newstitle > span > b:nth-child(1)::text').extract()[0]
        news['ctime'] = strptime_helper(ctime_str, '：%Y/%m/%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
