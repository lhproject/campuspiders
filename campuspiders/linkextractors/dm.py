#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import itertools
import lxml.html
import pyquery

from scrapy.link import Link
from scrapy.utils.python import unique


class DMHomepageLinkExtractor(object):
    def _extract_links(self, response_text, response_url):
        html = lxml.html.fromstring(response_text)
        html.make_links_absolute(response_url)
        sel = pyquery.PyQuery(html)

        evt_links = sel('.news > li:not(.more) > a')
        ann_links = sel('.announcement > li:not(.more) > a')

        all_links = [
                Link(elem.attrib['href'], text=elem.text)
                for elem in itertools.chain(evt_links, ann_links)
                ]

        return unique(all_links, key=lambda link: link.url)

    def extract_links(self, response):
        return self._extract_links(response.body, response.url)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
