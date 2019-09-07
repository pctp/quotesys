#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import request
import json
import jimit as ji

from models import Rules


__author__ = 'James Iter'
__date__ = '2018/8/1'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class Base(object):

    def __init__(self, the_class=None, the_blueprint=None, the_blueprints=None):
        self.the_class = the_class
        self.the_blueprint = the_blueprint
        self.the_blueprints = the_blueprints

    def get(self, ids=None, ids_rule=None, by_field=None):
        the_instance = self.the_class()

        args_rules = [
            ids_rule
        ]

        try:
            ji.Check.previewing(args_rules, {ids_rule[1]: ids})

            ret = dict()
            ret['state'] = ji.Common.exchange_state(20000)

            if -1 == ids.find(','):
                setattr(the_instance, by_field, ids)
                the_instance.get_by(by_field)
                ret['data'] = the_instance.__dict__

            else:
                ret['data'], ret['total'] = self.the_class.get_by_filter(
                    limit=100, order_by=by_field, filter_str=':'.join([by_field, 'in', ids]))

            return ret
        except ji.PreviewingError, e:
            return json.loads(e.message)

    def get_by_filter(self):
        page = str(request.args.get('page', 1))
        page_size = str(request.args.get('page_size', 50))

        args_rules = [
            Rules.PAGE.value,
            Rules.PAGE_SIZE.value
        ]

        try:
            ji.Check.previewing(args_rules, {'page': page, 'page_size': page_size})
        except ji.PreviewingError, e:
            return json.loads(e.message)

        page = int(page)
        page_size = int(page_size)

        # 把page和page_size换算成offset和limit
        offset = (page - 1) * page_size
        # offset, limit将覆盖page及page_size的影响
        offset = str(request.args.get('offset', offset))
        limit = str(request.args.get('limit', page_size))

        order_by = request.args.get('order_by', 'id')
        order = request.args.get('order', 'asc')
        filter_str = request.args.get('filter', '')

        args_rules = [
            Rules.OFFSET.value,
            Rules.LIMIT.value,
            Rules.ORDER_BY.value,
            Rules.ORDER.value
        ]

        try:
            ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order})
            offset = int(offset)
            limit = int(limit)
            ret = dict()
            ret['state'] = ji.Common.exchange_state(20000)
            ret['data'] = list()
            ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size,
                             'next': '', 'prev': '', 'first': '', 'last': ''}

            ret['data'], ret['paging']['total'] = self.the_class.get_by_filter(
                offset=offset, limit=limit, order_by=order_by, order=order, filter_str=filter_str)

            host_url = request.host_url.rstrip('/')
            other_str = '&filter=' + filter_str + '&order=' + order + '&order_by=' + order_by
            last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

            if page <= 1:
                ret['paging']['prev'] = host_url + self.the_blueprints.url_prefix + '?page=1&page_size=' + \
                                        page_size.__str__() + other_str
            else:
                ret['paging']['prev'] = host_url + self.the_blueprints.url_prefix + '?page=' + str(page - 1) + \
                                        '&page_size=' + page_size.__str__() + other_str

            if page >= last_pagination:
                ret['paging']['next'] = host_url + self.the_blueprints.url_prefix + '?page=' + \
                                        last_pagination.__str__() + '&page_size=' + page_size.__str__() + other_str
            else:
                ret['paging']['next'] = host_url + self.the_blueprints.url_prefix + '?page=' + str(page + 1) + \
                                        '&page_size=' + page_size.__str__() + other_str

            ret['paging']['first'] = host_url + self.the_blueprints.url_prefix + '?page=1&page_size=' + \
                page_size.__str__() + other_str
            ret['paging']['last'] = \
                host_url + self.the_blueprints.url_prefix + '?page=' + last_pagination.__str__() + '&page_size=' + \
                page_size.__str__() + other_str

            return ret
        except ji.PreviewingError, e:
            return json.loads(e.message)

    def content_search(self):
        page = str(request.args.get('page', 1))
        page_size = str(request.args.get('page_size', 50))

        args_rules = [
            Rules.PAGE.value,
            Rules.PAGE_SIZE.value
        ]

        try:
            ji.Check.previewing(args_rules, {'page': page, 'page_size': page_size})
        except ji.PreviewingError, e:
            return json.loads(e.message)

        page = int(page)
        page_size = int(page_size)

        # 把page和page_size换算成offset和limit
        offset = (page - 1) * page_size
        # offset, limit将覆盖page及page_size的影响
        offset = str(request.args.get('offset', offset))
        limit = str(request.args.get('limit', page_size))

        order_by = request.args.get('order_by', 'id')
        order = request.args.get('order', 'asc')
        keyword = request.args.get('keyword', '')

        args_rules = [
            Rules.OFFSET.value,
            Rules.LIMIT.value,
            Rules.ORDER_BY.value,
            Rules.ORDER.value,
            Rules.KEYWORD.value
        ]

        try:
            ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order,
                                             'keyword': keyword})
            offset = int(offset)
            limit = int(limit)
            ret = dict()
            ret['state'] = ji.Common.exchange_state(20000)
            ret['data'] = list()
            ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size}

            ret['data'], ret['paging']['total'] = self.the_class.content_search(
                offset=offset, limit=limit, order_by=order_by, order=order, keyword=keyword)

            host_url = request.host_url.rstrip('/')
            other_str = '&keyword=' + keyword + '&order=' + order + '&order_by=' + order_by
            last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

            if page <= 1:
                ret['paging']['prev'] = host_url + self.the_blueprints.url_prefix + '/_search?page=1&page_size=' + \
                                        page_size.__str__() + other_str
            else:
                ret['paging']['prev'] = host_url + self.the_blueprints.url_prefix + '/_search?page=' + str(page - 1) + \
                                        '&page_size=' + page_size.__str__() + other_str

            if page >= last_pagination:
                ret['paging'][
                    'next'] = host_url + self.the_blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + \
                              '&page_size=' + page_size.__str__() + other_str
            else:
                ret['paging']['next'] = host_url + self.the_blueprints.url_prefix + '/_search?page=' + str(page + 1) + \
                                        '&page_size=' + page_size.__str__() + other_str

            ret['paging']['first'] = host_url + self.the_blueprints.url_prefix + '/_search?page=1&page_size=' + \
                page_size.__str__() + other_str
            ret['paging']['last'] = \
                host_url + self.the_blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + \
                '&page_size=' + page_size.__str__() + other_str

            return ret
        except ji.PreviewingError, e:
            return json.loads(e.message)

    def delete(self, ids=None, ids_rule=None, by_field=None):
        the_instance = self.the_class()

        args_rules = [
            ids_rule
        ]

        try:
            ji.Check.previewing(args_rules, {ids_rule[1]: ids})

            ret = dict()
            ret['state'] = ji.Common.exchange_state(20000)

            the_instance.delete_by_filter(filter_str=':'.join([by_field, 'in', ids]))

            return ret
        except ji.PreviewingError, e:
            return json.loads(e.message)

