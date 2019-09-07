#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback

import mysql.connector
import mysql.connector.pooling
import redis
from mysql.connector import errorcode
import time
import jimit as ji

from initialize import app, logger


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class Database(object):

    cnxpool = None
    r = None

    def __init__(self):
        pass

    @classmethod
    def init_conn_mysql(cls):
        try:
            cls.cnxpool = mysql.connector.pooling.MySQLConnectionPool(
                host=app.config["db_host"],
                user=app.config["db_user"],
                password=app.config["db_password"],
                port=app.config["db_port"],
                database=app.config["db_name"],
                raise_on_warnings=app.config["DEBUG"],
                pool_size=app.config["db_pool_size"],
                charset=app.config["db_charset"]
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                e_msg = u'用户名或密码错误'
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                e_msg = u'数据库不存在'
            else:
                e_msg = err.msg

            logger.error(e_msg)
            exit(err.errno)

    @classmethod
    def keepalived_mysql(cls):
        def ping(label='', _cnxpool=None):
            if _cnxpool is None:
                logger.critical(''.join(['cnxpool must not None by ', label]))
                return

            try:
                _cnx = _cnxpool.get_connection()
                _cnx.ping(attempts=1, delay=0)
            except mysql.connector.errors.InterfaceError as err:
                logger.critical(err.msg)
            except mysql.connector.Error as err:
                logger.error(err)
            else:
                _cnx.close()

        while True:
            try:
                time.sleep(5)
                ping(label='', _cnxpool=cls.cnxpool)
            except:
                logger.error(traceback.format_exc())

    @classmethod
    def init_conn_redis(cls):
        """
          * Added TCP Keep-alive support by passing use the socket_keepalive=True
            option. Finer grain control can be achieved using the
            socket_keepalive_options option which expects a dictionary with any of
            the keys (socket.TCP_KEEPIDLE, socket.TCP_KEEPCNT, socket.TCP_KEEPINTVL)
            and integers for values. Thanks Yossi Gottlieb.
            TCP_KEEPDILE 设置连接上如果没有数据发送的话，多久后发送keepalive探测分组，单位是秒
            TCP_KEEPINTVL 前后两次探测之间的时间间隔，单位是秒
            TCP_KEEPCNT 关闭一个非活跃连接之前的最大重试次数
        """
        import socket
        cls.r = redis.StrictRedis(host=app.config.get('redis_host', '127.0.0.1'),
                                  port=app.config.get('redis_port', 6379),
                                  db=app.config.get('redis_dbid', 0), decode_responses=True, socket_timeout=600,
                                  socket_connect_timeout=600, socket_keepalive=True,
                                  socket_keepalive_options={socket.TCP_KEEPIDLE: 2, socket.TCP_KEEPINTVL: 5,
                                                            socket.TCP_KEEPCNT: 10},
                                  retry_on_timeout=True)

        try:
            cls.r.ping()
        except redis.exceptions.ResponseError as e:
            logger.warn(e.message)
            cls.r = redis.StrictRedis(host=app.config.get('redis_host', '127.0.0.1'),
                                      port=app.config.get('redis_port', 6379),
                                      db=app.config.get('redis_dbid', 0), password=app.config.get('redis_password', ''),
                                      decode_responses=True, socket_timeout=600,
                                      socket_connect_timeout=600, socket_keepalive=True,
                                      socket_keepalive_options={socket.TCP_KEEPIDLE: 2, socket.TCP_KEEPINTVL: 5,
                                                                socket.TCP_KEEPCNT: 10},
                                      retry_on_timeout=True)

        cls.r.client_setname(ji.Common.get_hostname())

    @classmethod
    def keepalived_redis(cls):
        while True:
            try:
                time.sleep(5)
                cls.r.ping()

            except redis.exceptions.ConnectionError as e:
                logger.error(e.message)
                cls.init_conn_redis()

            except:
                logger.error(traceback.format_exc())

