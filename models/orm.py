#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import jimit as ji
from mysql.connector import errorcode, errors

from database import Database as db
from models import Filter


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class ORM(object):

    _table_name = None
    _primary_key = None

    def __init__(self):
        pass

    def create(self):
        sql_stmt = ("INSERT INTO " + self._table_name + " (" +
                    ', '.join(filter(lambda _key: _key != self._primary_key, self.__dict__.keys())) +
                    ") VALUES (" +
                    ', '.join(['%({0})s'.format(key)
                               for key in filter(lambda _key: _key != self._primary_key, self.__dict__.keys())]) + ")")

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            cnx.commit()
        except errors.IntegrityError, e:
            ret = dict()
            if e.errno == errorcode.ER_DUP_ENTRY:
                ret['state'] = ji.Common.exchange_state(40901)
            elif e.errno == errorcode.ER_BAD_NULL_ERROR:
                ret['state'] = ji.Common.exchange_state(41202)
            else:
                ret['state'] = ji.Common.exchange_state(50002)

            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', e.msg])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        finally:
            cursor.close()
            cnx.close()

    def update(self):

        if not self.exist():
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', self._primary_key.__str__()])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        sql_stmt = ("UPDATE " + self._table_name + " SET " +
                    ', '.join(['{0} = %({0})s'.format(key)
                               for key in filter(lambda _key: _key != self._primary_key, self.__dict__.keys())]) +
                    " WHERE " + '{0} = %({0})s'.format(self._primary_key))

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            cnx.commit()
        except errors.IntegrityError, e:
            ret = dict()
            if e.errno == errorcode.ER_DUP_ENTRY:
                ret['state'] = ji.Common.exchange_state(40901)
            elif e.errno == errorcode.ER_BAD_NULL_ERROR:
                ret['state'] = ji.Common.exchange_state(41202)
            else:
                ret['state'] = ji.Common.exchange_state(50002)

            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', e.msg])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        finally:
            cursor.close()
            cnx.close()

    def delete(self):
        if not self.exist():
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', self._primary_key.__str__()])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        sql_stmt = ("DELETE FROM " + self._table_name + " WHERE " + '{0} = %({0})s'.format(self._primary_key))

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            cnx.commit()
        finally:
            cursor.close()
            cnx.close()

    def get(self):
        sql_stmt = ("SELECT " + ', '.join(self.__dict__.keys()) + " FROM " + self._table_name +
                    " WHERE " + '{0} = %({0})s'.format(self._primary_key) +
                    " LIMIT 1")

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            row = cursor.fetchone()
        finally:
            cursor.close()
            cnx.close()

        if isinstance(row, dict):
            self.__dict__ = row
        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ': '.join([ret['state']['sub']['zh-cn'], self._primary_key,
                                                      self.__getattribute__(self._primary_key).__str__()])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

    def exist(self):
        sql_stmt = ("SELECT " + self._primary_key + " FROM " + self._table_name +
                    " WHERE " + '{0} = %({0})s'.format(self._primary_key) + " LIMIT 1")

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            row = cursor.fetchone()
        finally:
            cursor.close()
            cnx.close()

        if isinstance(row, dict):
            return True

        return False

    def get_by(self, field):
        sql_stmt = ("SELECT " + ', '.join(self.__dict__.keys()) +
                    " FROM " + self._table_name + " WHERE " + '{0} = %({0})s'.format(field) + " LIMIT 1")

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            row = cursor.fetchone()
        finally:
            cursor.close()
            cnx.close()

        if isinstance(row, dict):
            self.__dict__ = row
        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            ret['state']['sub']['zh-cn'] = ': '.join([ret['state']['sub']['zh-cn'], field.__str__(),
                                                      self.__getattribute__(field).__str__()])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

    def exist_by(self, field):
        sql_field = field + ' = %(' + field + ')s'
        sql_stmt = ("SELECT " + self._primary_key + " FROM " + self._table_name + " WHERE " + sql_field + " LIMIT 1")

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, self.__dict__)
            row = cursor.fetchone()
        finally:
            cursor.close()
            cnx.close()

        if isinstance(row, dict):
            return True

        return False

    @staticmethod
    def get_filter_keywords():
        # 指定参与过滤的关键字及其数据库对应字段类型
        """
        使用示例
        return {
            'name': FilterFieldType.STR.value,
            'remark': FilterFieldType.STR.value,
            'age': FilterFieldType.INT.value
        }
        """
        raise NotImplementedError()

    @classmethod
    def get_by_filter(cls, offset=0, limit=1000, order_by=None, order='asc', filter_str=''):
        if order_by is None:
            order_by = cls._primary_key

        sql_stmt = ("SELECT * FROM " + cls._table_name + " ORDER BY " + order_by + " " + order +
                    " LIMIT %(offset)s, %(limit)s")
        sql_stmt_count = ("SELECT count(" + cls._primary_key + ") FROM " + cls._table_name)

        where_str = Filter.filter_str_to_sql(allow_keywords=cls.get_filter_keywords(), filter_str=filter_str)
        if where_str != '':
            sql_stmt = ("SELECT * FROM " + cls._table_name + " WHERE " + where_str + " ORDER BY " + order_by + " " +
                        order + " LIMIT %(offset)s, %(limit)s")
            sql_stmt_count = ("SELECT count(" + cls._primary_key + ") FROM " + cls._table_name + " WHERE " + where_str)

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, {'offset': offset, 'limit': limit})
            rows = cursor.fetchall()
            cursor.execute(sql_stmt_count)
            count = cursor.fetchone()
            return rows, count["count(" + cls._primary_key + ")"]
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def get_allow_update_keywords():
        # 指定允许批量更新的字段
        """
        使用示例
        return ['remark', 'age']
        """
        raise NotImplementedError()

    @classmethod
    def update_by_filter(cls, kv, filter_str=''):
        # 过滤掉不予支持批量更新的字段
        _kv = {}
        for k, v in kv.iteritems():
            if k in cls.get_allow_update_keywords():
                _kv[k] = v

        if _kv.__len__() < 1:
            return

        # set_str = ', '.join(map(lambda x: x + ' = %(' + x + ')s', _kv.keys()))
        # 上面为通过map实现的方式
        set_str = ', '.join(['{0} = %({0})s'.format(key) for key in _kv.keys()])
        where_str = Filter.filter_str_to_sql(allow_keywords=cls.get_filter_keywords(), filter_str=filter_str)
        sql_stmt = ("UPDATE " + cls._table_name + " SET " + set_str + " WHERE " + where_str)

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, _kv)
            cnx.commit()
        finally:
            cursor.close()
            cnx.close()

    @classmethod
    def delete_by_filter(cls, filter_str=''):
        where_str = Filter.filter_str_to_sql(allow_keywords=cls.get_filter_keywords(), filter_str=filter_str)
        sql_stmt = ("DELETE FROM " + cls._table_name + " WHERE " + where_str)

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt)
            cnx.commit()
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def get_allow_content_search_keywords():
        # 指定允许全文检索的字段
        """
        使用示例
        return ['name', 'remark']
        """
        raise NotImplementedError()

    @classmethod
    def content_search(cls, offset=0, limit=1000, order_by=None, order='asc', keyword=''):
        if order_by is None:
            order_by = cls._primary_key

        _kv = dict()
        _kv = _kv.fromkeys(cls.get_allow_content_search_keywords(), '%{0}%'.format(keyword))
        where_str = ' OR '.join([k + ' LIKE %(' + k + ')s' for k in _kv.keys()])
        sql_stmt = ("SELECT * FROM " + cls._table_name + " WHERE " + where_str + " ORDER BY " + order_by + " " + order +
                    " LIMIT %(offset)s, %(limit)s")
        sql_stmt_count = ("SELECT count(" + cls._primary_key + ") FROM " + cls._table_name + " WHERE " + where_str)

        _kv.update({'offset': offset, 'limit': limit})
        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt, _kv)
            rows = cursor.fetchall()
            cursor.execute(sql_stmt_count, _kv)
            count = cursor.fetchone()
            return rows, count["count(" + cls._primary_key + ")"]
        finally:
            cursor.close()
            cnx.close()

    @classmethod
    def get_all(cls, order_by=None, order='asc'):
        if order_by is None:
            order_by = cls._primary_key

        sql_stmt = ("SELECT * FROM " + cls._table_name + " ORDER BY " + order_by + " " + order)
        sql_stmt_count = ("SELECT count(" + cls._primary_key + ") FROM " + cls._table_name)

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt)
            rows = cursor.fetchall()
            cursor.execute(sql_stmt_count)
            count = cursor.fetchone()
            return rows, count["count(" + cls._primary_key + ")"]
        finally:
            cursor.close()
            cnx.close()

    @classmethod
    def distinct_by(cls, fields=None, order_by=None, order='asc'):
        if order_by is None:
            order_by = cls._primary_key

        assert isinstance(fields, list)

        sql_stmt = ("SELECT DISTINCT " + ', '.join(fields) + " FROM " + cls._table_name +
                    " ORDER BY " + order_by + " " + order)

        cnx = db.cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(sql_stmt)
            rows = cursor.fetchall()
            return rows, rows.__len__()
        finally:
            cursor.close()
            cnx.close()

