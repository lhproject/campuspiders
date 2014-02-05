#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from ..utils.helpers import strptime_helper, normalize_content
from ..items import NewsItem

# 注: 此站还是通元 CMS
SOURCE_ID_HQ = 'hq'


class HQNewsSpider(CrawlSpider):
    name = 'hq'
    allowed_domains = ['hq.jiangnan.edu.cn', ]
    start_urls = ['http://hq.jiangnan.edu.cn/xwzx/tzgg/', ]
    rules = [
            Rule(SgmlLinkExtractor(allow=[r'/xwzx/tzgg/\d+.shtml']), 'parse_news_item'),
            ]

    def parse_news_item(self, response):
        sel = Selector(response)
        news = NewsItem()

        news['url'] = response.url
        news['source'] = SOURCE_ID_HQ

        news['title'] = sel.css('.con_head_infor > h1::text').extract()[0]
        news['content'] = normalize_content(sel.css('#zoom ::text').extract())

        # 作者 (编辑) 和发布者 (来源) 都写出来, 简直业界良心!
        # 来源字段形如: u' 来源：admin ', 先去掉首尾空格
        # 此字段也可能不存在, 此时的 extract() 结果是空列表
        author_str = ''.join(sel.css('.con_head_infor > p > span:nth-child(2)::text').extract()).strip()
        news['author'] = author_str[3:] if len(author_str) > 3 else ''

        # 编辑字段形如: u'编辑: 信息化中心'
        # 这里姑且也像来源字段一样考虑下字段不存在的情况吧
        publisher_str = ''.join(sel.css('.con_head_infor > p > span:nth-child(5)::text').extract()).strip()
        news['publisher'] = publisher_str[4:] if len(publisher_str) > 4 else ''

        # 发布时间字段形如: u'发布时间:2013-12-26'
        ctime_str = sel.css('.con_head_infor > p > span:nth-child(3)::text').extract()[0][5:]
        news['ctime'] = strptime_helper(ctime_str, '%Y-%m-%d')

        return news


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
