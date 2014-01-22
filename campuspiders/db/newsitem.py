#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

__all__ = [
        'NewsItemRecord',
        ]

import six
import hashlib
import time

from weiyu.db.mapper.base import Document

_number_types = tuple([float] + list(six.integer_types))

NEWS_ITEM_STRUCT_ID = 'campuspiders.news'

DATE_INDEX_ZSET_KEY = 'idx:date'
ITEM_KEY_FORMAT = 'item:%s:%s'

# TODO: 这个要不要移到 Rainfile 配置里?
ITEM_CACHE_DURATION = 86400


def extract_ymd(timestamp):
    '''从传入的 Unix 时间戳解析出当前系统时区下表示的年月日.'''

    # NOTE: 时区问题就不管了, 承载系统各部分的节点需要一致的时区设置
    result = time.localtime(timestamp)
    return result.tm_year, result.tm_mon, result.tm_mday


def gen_item_id(item):
    '''生成文章项的 Redis hash ID.'''

    # 统一一下格式
    url_hash = hashlib.sha1(item['url']).hexdigest()

    return ITEM_KEY_FORMAT % (item['source'], url_hash, )


class NewsItemRecord(Document):
    '''新闻文章对象.

    本结构存储后端应该配置为 Redis.

    '''

    struct_id = NEWS_ITEM_STRUCT_ID

    @classmethod
    def get_recent_items(cls, from_ts):
        '''从数据库获取发布时间从所指定时间戳开始, 到当前为止的新闻项.'''

        with cls.storage as conn:
            ids = conn.zrevrangebyscore(DATE_INDEX_ZSET_KEY, '+inf', from_ts)

            for item_id in ids:
                obj = conn.hgetall(item_id)

                # 直接返回 decode 出来的裸 dict, 因为这个功能设计出来数据就
                # 不是供修改的, 就没必要拿这个 Document 包一层了
                yield cls.decode(obj)

    def save(self):
        '''向数据库中存储本条记录并更新时序索引.'''

        new_id = gen_item_id(self)

        with self.storage as conn:
            pipeline = conn.pipeline()

            # 记录本体
            pipeline.hmset(new_id, self.encode())
            pipeline.expire(new_id, ITEM_CACHE_DURATION)

            # 时序索引
            pipeline.zadd(DATE_INDEX_ZSET_KEY, self['ctime'], new_id)

            pipeline.execute()

        self['id'] = new_id

    @classmethod
    def purge_old_index(cls):
        '''从时序索引中删去已经失效的项.'''

        with cls.storage as conn:
            curtime = int(time.time())
            expire_time = curtime - ITEM_CACHE_DURATION

            # 删掉权重 (时间戳) 小于 (早于) 当前时间减去存活时间的索引记录
            # 文档不用管, 当然消失了
            return conn.zremrangebyscore(
                    DATE_INDEX_ZSET_KEY,
                    '-inf',
                    expire_time,
                    )


@NewsItemRecord.decoder(1)
def news_item_dec_v1(data):
    return {
            'source': data['src'],
            'url': data['url'],
            'ctime': data['ctm'],
            'fetch_time': data['fet'],
            'title': data['title'],
            'content': data['cnt'],
            }


@NewsItemRecord.encoder(1)
def news_item_enc_v1(item):
    assert 'source' in item
    assert isinstance(item['source'], six.text_type)
    assert 'url' in item
    assert isinstance(item['url'], six.text_type)
    assert 'ctime' in item
    assert isinstance(item['ctime'], _number_types)
    assert 'fetch_time' in item
    assert isinstance(item['fetch_time'], _number_types)
    assert 'title' in item
    assert isinstance(item['title'], six.text_type)
    assert 'content' in item
    assert isinstance(item['content'], six.text_type)

    return {
            'src': item['source'],
            'url': item['url'],
            'ctm': item['ctime'],
            'fet': item['fetch_time'],
            'title': item['title'],
            'cnt': item['content'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
