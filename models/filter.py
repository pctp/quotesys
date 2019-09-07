#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import Enum

from initialize import regex_sql_str, regex_dsl_str


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class FilterFieldType(Enum):
    INT = 'int'
    STR = 'str'
    BOOL = 'bool'


class Filter(object):
    operator = {'eq': '=',
                'gt': '>',
                'lt': '<',
                'ne': '!=',
                'in': 'in',
                'notin': 'not in',
                'like': 'like'}

    def __init__(self):
        pass

    @staticmethod
    def get_fit_statement(field_type=None, value=''):
        if field_type == FilterFieldType.INT.value:
            if not value.lstrip('-').isdigit():
                raise TypeError(''.join(['Value: ', str(value), ' should be digit']))
            return value
        elif field_type == FilterFieldType.STR.value:
            _s = regex_sql_str.sub('"', str(value)).strip('"')
            return ''.join(['"', _s.replace('"', '\\"'), '"'])
        elif field_type == FilterFieldType.BOOL.value:
            return str(False) if value.lower() == 'false' else str(True)
        else:
            raise TypeError(''.join(['unknown type ', str(field_type)]))

    @classmethod
    def dsl_to_sql(cls, allow_keywords=None, dsl=''):
        sql_stmt = ''

        if regex_dsl_str.match(dsl) is None:
            return sql_stmt

        keyword, operator, value = dsl.split(':', 2)
        operator = operator.lower()

        if keyword not in allow_keywords.keys():
            return sql_stmt
        field_type = allow_keywords[keyword]

        if operator in ['eq', 'gt', 'lt', 'ne']:
            sql_stmt = keyword + cls.operator[operator] + cls.get_fit_statement(field_type=field_type, value=value)

        elif operator == 'in':
            # from itertools import repeat
            # _sql_stmt = map(cls.get_fit_statement, repeat(field_type, len(value.split(','))), value.split(','))
            # 上面为通过map实现的方式
            _sql_stmt = [cls.get_fit_statement(field_type=field_type, value=v) for v in value.split(',')]
            sql_stmt = keyword + ' in (' + ','.join(_sql_stmt) + ')'

        elif operator == 'notin':
            _sql_stmt = [cls.get_fit_statement(field_type=field_type, value=v) for v in value.split(',')]
            sql_stmt = keyword + ' not in (' + ','.join(_sql_stmt) + ')'

        elif operator == 'like':
            sql_stmt = keyword + ' like "%' + cls.get_fit_statement(
                field_type=field_type, value=value).strip('"') + '%"'

        return sql_stmt

    @classmethod
    def filter_str_to_sql(cls, allow_keywords=None, filter_str=''):
        sql_stmts = []
        for dsl in filter_str.split(';'):
            sql_stmt = cls.dsl_to_sql(allow_keywords=allow_keywords, dsl=dsl)
            if sql_stmt == '':
                continue

            sql_stmts.append(sql_stmt)

        return ' AND '.join(sql_stmts)

