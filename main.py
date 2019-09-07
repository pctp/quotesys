#!/usr/bin/env python
# -*- coding: utf-8 -*-


import traceback
import signal

import time
from datetime import timedelta
import jimit as ji
import json

from flask import request

try:
    from flask_session import Session
except ImportError as e:
    # 兼容老版本
    from flask.ext.session import Session

from werkzeug.debug import get_current_traceback

from models import Utils
from models.initialize import logger, app
import api_route_table
from models import Database as db

from api.ohlc import blueprint as ohlc_blueprint
from api.ohlc import blueprints as ohlc_blueprints


__author__ = 'James Iter'
__date__ = '2018/8/1'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


@app.after_request
@Utils.dumps2response
def r_after_request(response):
    try:
        # https://developer.mozilla.org/en/HTTP_access_control
        # (中文版) https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS#Access-Control-Allow-Credentials
        # http://www.w3.org/TR/cors/
        # 由于浏览器同源策略，凡是发送请求url的协议、域名、端口三者之间任意一与当前页面地址不同即为跨域。

        if request.referrer is None:
            # 跑测试脚本时，用该规则。
            response.headers['Access-Control-Allow-Origin'] = '*'
        else:
            # 生产环境中，如果前后端分离。那么请指定具体的前端域名地址，不要用如下在开发环境中的便捷方式。
            # -- Access-Control-Allow-Credentials为true，携带cookie时，不允许Access-Control-Allow-Origin为通配符，是浏览器对用户的一种安全保护。
            # -- 至少能避免登录山寨网站，骗取用户相关信息。
            response.headers['Access-Control-Allow-Origin'] = '/'.join(request.referrer.split('/')[:3])

        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, DELETE, OPTIONS, PATCH, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'X-Request-With, Content-Type'
        response.headers['Access-Control-Expose-Headers'] = 'Set-Cookie'

        return response
    except ji.JITError, e:
        return json.loads(e.message)


@app.teardown_request
def teardown_request(exception):
    if exception:
        _traceback = get_current_traceback()
        logger.error(_traceback.plaintext)


# noinspection PyBroadException
try:
    db.init_conn_redis()

    app.register_blueprint(ohlc_blueprint)
    app.register_blueprint(ohlc_blueprints)

except:
    logger.error(traceback.format_exc())

# noinspection PyBroadException
try:
    signal.signal(signal.SIGTERM, Utils.signal_handle)
    signal.signal(signal.SIGINT, Utils.signal_handle)

except:
    logger.error(traceback.format_exc())
    exit(-1)


if __name__ == '__main__':
    # noinspection PyBroadException
    try:

        app.run(host=app.config['listen'], port=app.config['port'], use_reloader=False, threaded=True)

        while True:
            if Utils.exit_flag:
                # 主线程即将结束
                break
            time.sleep(1)

        print 'Main say bye-bye!'

    except:
        logger.error(traceback.format_exc())
        exit(-1)

