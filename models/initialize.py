#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Flask
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import os
import sys
import getopt
import re
import errno


reload(sys)
sys.setdefaultencoding('utf8')


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.jinja_env.add_extension('jinja2.ext.i18n')
app.jinja_env.add_extension('jinja2.ext.do')


class Init(object):
    config = {
        'config_file': '/etc/awp.conf',
        'log_cycle': 'D',
        'data_stream_queue': 'Q:DataStream',
        'ipc_queue': 'Q:IPC',
        'db_charset': 'utf8',
        'db_pool_size': 10,
        'DEBUG': False,
        'jwt_algorithm': 'HS512',
        'token_ttl': 604800,
        'SESSION_TYPE': 'filesystem',
        'SESSION_PERMANENT': True,
        'SESSION_USE_SIGNER': True,
        'SESSION_FILE_DIR': '/tmp/jimv',
        'SESSION_FILE_THRESHOLD': 5000,
        'SESSION_COOKIE_NAME': 'sid',
        'SESSION_COOKIE_SECURE': False,
        'PERMANENT_SESSION_LIFETIME': 604800
    }

    @classmethod
    def load_config(cls):

        def usage():
            print "Usage:%s [-f] [--config_file]" % sys.argv[0]

        opts = None
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hc:n:s:',
                                       ['help', 'config_file='])
        except getopt.GetoptError as e:
            print str(e)
            usage()
            exit(e.message.__len__())

        for k, v in opts:
            if k in ("-h", "--help"):
                usage()
                exit()
            elif k in ("-f", "--config_file"):
                cls.config['config_file'] = v
            else:
                pass

        if not os.path.isfile(cls.config['config_file']):
            raise SystemError(u'配置文件不存在, 请指明配置文件路径')

        with open(cls.config['config_file'], 'r') as f:
            cls.config.update(json.load(f))

        return cls.config

    @classmethod
    def init_logger(cls):
        log_dir = os.path.dirname(cls.config['log_file_path'])
        if not os.path.isdir(log_dir):
            try:
                os.makedirs(log_dir, 0755)
            except OSError as e:
                # 如果配置文件中的日志目录无写入权限，则调整日志路径到本项目目录下
                if e.errno != errno.EACCES:
                    raise

                cls.config['log_file_path'] = './logs/awp.log'
                log_dir = os.path.dirname(cls.config['log_file_path'])

                if not os.path.isdir(log_dir):
                    os.makedirs(log_dir, 0755)

                print u'日志路径自动调整为 ' + cls.config['log_file_path']

        _logger = logging.getLogger(cls.config['log_file_path'])

        if cls.config['DEBUG']:
            _logger.setLevel(logging.DEBUG)
        else:
            _logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(cls.config['log_file_path'], when=cls.config['log_cycle'],
                                      interval=1, backupCount=7)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
        fh.setFormatter(formatter)
        _logger.addHandler(fh)
        return _logger


# 预编译效率更高
regex_sql_str = re.compile('\\\+"')
regex_dsl_str = re.compile('^\w+:\w+:[\S| ]+$')

config = Init.load_config()
logger = Init.init_logger()

app.config = dict(app.config, **config)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
