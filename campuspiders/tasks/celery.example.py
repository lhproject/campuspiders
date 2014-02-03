#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, division

import os

from celery import Celery

from weiyu.init import load_config

# 走到项目根目录, 那里有配置文件
project_root = os.path.join(os.path.dirname(__file__),  '../..')
os.chdir(project_root)
load_config()


class CeleryConfig(object):
    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE = 'Asia/Shanghai'

    CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml', ]

    BROKER_URL = 'redis://localhost:6379/13'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/14'
    CELERY_IMPORTS = (
            'campuspiders.tasks.newsitem',
            )


app = Celery('campuspiders')
app.config_from_object(CeleryConfig)


if __name__ == '__main__':
    celery.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
