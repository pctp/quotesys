#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from copy import deepcopy
import Queue
import json

from models import Utils
from models import Database as db
from models.initialize import app, logger


if sys.platform == 'win32':
    from ctp_win32 import ApiStruct, MdApi, TraderApi

elif sys.platform == 'linux2':
    from ctp_linux64 import ApiStruct, MdApi, TraderApi


__author__ = 'James Iter'
__date__ = '2018/4/22'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


db.init_conn_redis()


inst = [u'AP810', u'rb1810']
BROKER_ID = '9999'
INVESTOR_ID = '116667'
PASSWORD = '110.com'
ADDRESS_MD = 'tcp://180.168.146.187:10031'

q_depth_market_data = Queue.Queue()

granularities = [60, 120, 300, 600, 1800]


class MyMdApi(MdApi):
    def __init__(self, instruments, broker_id,
                 investor_id, password, *args, **kwargs):
        self.request_id = 0
        self.instruments = instruments
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password

    def OnRspError(self, info, request_id, is_last):
        print " Error: " + info

    @staticmethod
    def is_error_rsp_info(info):
        if info.ErrorID != 0:
            print "ErrorID=", info.ErrorID, ", ErrorMsg=", info.ErrorMsg
        return info.ErrorID != 0

    def OnHeartBeatWarning(self, _time):
        print "onHeartBeatWarning", _time

    def OnFrontConnected(self):
        print "OnFrontConnected:"
        self.user_login(self.broker_id, self.investor_id, self.password)

    def user_login(self, broker_id, investor_id, password):
        req = ApiStruct.ReqUserLogin(BrokerID=broker_id, UserID=investor_id, Password=password)

        self.request_id += 1
        ret = self.ReqUserLogin(req, self.request_id)

    def OnRspUserLogin(self, user_login, info, rid, is_last):
        print "OnRspUserLogin", is_last, info

        if is_last and not self.is_error_rsp_info(info):
            print "get today's action day:", repr(self.GetTradingDay())
            self.subscribe_market_data(self.instruments)

    def subscribe_market_data(self, instruments):
        self.SubscribeMarketData(instruments)

    def OnRtnDepthMarketData(self, depth_market_data):
        q_depth_market_data.put(deepcopy(depth_market_data))


def login():
    # 登录行情服务器
    user = MyMdApi(instruments=inst, broker_id=BROKER_ID, investor_id=INVESTOR_ID, password=PASSWORD)
    user.Create("data")
    user.RegisterFront(ADDRESS_MD)
    user.Init()

    print u'行情服务器登录成功'

    while True:

        if Utils.exit_flag:
            msg = 'Thread CTPDataCollectEngine say bye-bye'
            print msg
            logger.info(msg=msg)

            return

        try:
            payload = q_depth_market_data.get(timeout=1)
            q_depth_market_data.task_done()

            awp_tick = {
                'granularities': granularities,
                'instrument_id': payload.InstrumentID,
                'last_price': payload.LastPrice,
                'action_day': payload.ActionDay,
                'update_time': payload.UpdateTime.replace(':', ''),
                'volume': payload.Volume
            }

            print awp_tick
            db.r.rpush(app.config['data_stream_queue'], json.dumps(awp_tick, ensure_ascii=False))

        except Queue.Empty as e:
            pass


if __name__ == "__main__":

    login()


