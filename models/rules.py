#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import Enum


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class Rules(Enum):
    # 正则表达式方便校验其来自URL的参数
    REG_NUMBER = 'regex:^\d{1,17}$'
    REG_NUMBERS = 'regex:^(\d{1,17})(,\d{1,17})*$'
    REG_UUIDS = 'regex:^([\w-]{36})(,[\w-]{36})*$'
    REG_IP = 'regex:^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$'

    OFFSET = (REG_NUMBER, 'offset')
    LIMIT = (REG_NUMBER, 'limit')
    PAGE = (REG_NUMBER, 'page')
    PAGE_SIZE = (REG_NUMBER, 'page_size')
    ORDER_BY = (basestring, 'order_by', (1, 30))
    ORDER = (basestring, 'order', ['asc', 'desc'])
    KEYWORD = (basestring, 'keyword')

    ID = (REG_NUMBER, 'id')
    IDS = (REG_NUMBERS, 'ids')

    TOKEN = (basestring, 'token')

