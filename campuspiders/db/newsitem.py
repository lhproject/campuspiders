#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

__all__ = [
        'NewsItemRecord',
        ]

import six
import hashlib
import time
import random

from weiyu.db.mapper.base import Document

from luohua.utils import radices

_number_types = tuple([float] + list(six.integer_types))

NEWS_ITEM_STRUCT_ID = 'campuspiders.news'

DATE_INDEX_ZSET_KEY = 'idx:date'
FETCH_TIME_INDEX_ZSET_KEY = 'idx:fetched'
SHORT_URL_HASH_KEY = 'hash:urls'
ITEM_KEY_FORMAT = 'item:%s:%s'

# TODO: 这个要不要移到 Rainfile 配置里?
ITEM_CACHE_DURATION = 86400

# 200000 篇文章最接近 62 进制 3 位数的极限了, 也够用了
TOTAL_SHORTURLS = 200000


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


def gen_shorturl_key():
    # 这里不是用于安全用途的随机数, 不必非得用 urandom 数据源
    return radices.to62(random.randint(1, TOTAL_SHORTURLS))


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
                # XXX: 不过微雨数据的版本字段需要先变成整数, 先这么着吧
                obj['_V'] = int(obj['_V'])
                yield cls.decode(obj)

    @classmethod
    def query_short_url(cls, short_url):
        '''转换短链到完整 URL.'''

        with cls.storage as conn:
            url = conn.hget(SHORT_URL_HASH_KEY, short_url)
            if url is None:
                # 这个短链映射不存在了
                return False, ''

            return True, url

    def save(self):
        '''向数据库中存储本条记录并更新时序索引.'''

        new_id = gen_item_id(self)

        with self.storage as conn:
            with conn.pipeline() as pipeline:
                # 记录本体
                pipeline.hmset(new_id, self.encode())
                pipeline.expire(new_id, ITEM_CACHE_DURATION)

                # 时序索引
                pipeline.zadd(DATE_INDEX_ZSET_KEY, self['ctime'], new_id)
                pipeline.zadd(FETCH_TIME_INDEX_ZSET_KEY, time.time(), new_id)

                pipeline.execute()

        self['id'] = new_id

    @classmethod
    def purge_old_index(cls):
        '''从时序索引中删去已经失效的项.'''

        with cls.storage as conn:
            expire_time = time.time() - ITEM_CACHE_DURATION

            # 删掉权重 (时间戳) 小于 (早于) 当前时间减去存活时间的索引记录
            # 文档不用管, 当然消失了
            gone_ids = conn.zrangebyscore(
                    FETCH_TIME_INDEX_ZSET_KEY,
                    '-inf',
                    expire_time,
                    )
            with conn.pipeline() as pipeline:
                pipeline.zrem(FETCH_TIME_INDEX_ZSET_KEY, *gone_ids)
                pipeline.zrem(DATE_INDEX_ZSET_KEY, *gone_ids)

                pipeline.execute()

    @classmethod
    def update_short_urls(cls):
        '''更新短链索引.'''

        with cls.storage as conn:
            # 扔掉旧索引
            conn.delete(SHORT_URL_HASH_KEY)

            # 遍历文章
            ids = conn.zrangebyscore(DATE_INDEX_ZSET_KEY, '-inf', '+inf')
            for item_id in ids:
                if not conn.exists(item_id):
                    # 文章的数据库记录已经消失了, 无视它继续
                    continue

                obj = conn.hgetall(item_id)
                # 这里使用了 get_recent_items 里一样的伎俩
                obj['_V'] = int(obj['_V'])
                item = cls.decode(obj)

                # 生成一个短链, 随机尝试 key 空间的 1/10000, 目前是 20 次
                short_url_created = False
                for tries in six.moves.range(TOTAL_SHORTURLS // 10000):
                    short_url = gen_shorturl_key()
                    short_url_created = conn.hsetnx(
                            SHORT_URL_HASH_KEY,
                            short_url,
                            item['url'],
                            ) == 1
                    if short_url_created:
                        break

                if not short_url_created:
                    # 尝试全都失败了? 不给这条记录生成了
                    continue

                # XXX: 泄漏了结构版本对结构内字段的抽象, 不过算了
                conn.hset(item_id, 's_url', short_url)


@NewsItemRecord.decoder(1)
def news_item_dec_v1(data):
    return {
            'source': data['src'],
            'url': data['url'],
            'ctime': float(data['ctm']),
            'fetch_time': float(data['fet']),
            'title': data['title'],
            'content': data['cnt'],
            'short_url': data['s_url'],
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

    # 短 URL
    if 'short_url' in item:
        assert isinstance(item['short_url'], six.text_type)
        short_url = item['short_url']
    else:
        short_url = ''

    return {
            'src': item['source'],
            'url': item['url'],
            'ctm': item['ctime'],
            'fet': item['fetch_time'],
            'title': item['title'],
            'cnt': item['content'],
            's_url': short_url,
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
