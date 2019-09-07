#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from copy import deepcopy
import Queue
from datetime import datetime
import time
import decimal

from models import Utils
from models.initialize import logger
from function import load_data_from_server, get_k_line_column, generate_ohlc_key, ma, cross, be_apart_from

if sys.platform == 'win32':
    from ctp_win32 import ApiStruct, MdApi, TraderApi

elif sys.platform == 'linux2':
    from ctp_linux64 import ApiStruct, MdApi, TraderApi

__author__ = 'James Iter'
__date__ = '2018/8/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'

inst = [u'rb1810']
BROKER_ID = '9999'
INVESTOR_ID = '116667'
PASSWORD = '110.com'
ADDRESS_MD = 'tcp://180.168.146.187:10031'

q_depth_market_data = Queue.Queue()

granularity = 120

data = None
nest = dict()


def init_data():
    global data
    data = load_data_from_server(server_base='http://106.14.119.122', instruments_id=inst[0], granularity=granularity)


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
        print
        "OnFrontConnected:"
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

    print
    u'行情服务器登录成功'

    while True:

        if Utils.exit_flag:
            msg = 'Thread CTPDataCollectEngine say bye-bye'
            print msg
            logger.info(msg=msg)

            return

        try:
            payload = q_depth_market_data.get(timeout=1)
            q_depth_market_data.task_done()

            action_day = payload.ActionDay
            instrument_id = payload.InstrumentID
            update_time = payload.UpdateTime.replace(':', '')
            last_price = float(payload.LastPrice)
            volume = payload.Volume

            if volume == 0:
                continue

            if update_time.find('.') != -1:
                dt = datetime.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S.%f")
                timestamp = time.mktime(dt.timetuple()) + (dt.microsecond / 1e6)

            else:
                timestamp = int(time.mktime(time.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S")))

            date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

            ohlc_key = generate_ohlc_key(instrument_id=instrument_id, granularity=granularity, timestamp=timestamp)

            if ohlc_key not in nest:
                nest[ohlc_key] = {
                    'date_time': date_time,
                    'last_timestamp': timestamp,
                    'high': last_price,
                    'low': last_price,
                    'close': last_price,
                    'open': last_price
                }

            nest[ohlc_key]['last_timestamp'] = timestamp
            nest[ohlc_key]['date_time'] = date_time

            nest[ohlc_key]['close'] = last_price

            if last_price > nest[ohlc_key]['high']:
                nest[ohlc_key]['high'] = last_price

            elif last_price < nest[ohlc_key]['low']:
                nest[ohlc_key]['low'] = last_price

            if nest.__len__() > 1:
                for k, v in nest.items():
                    if k == ohlc_key:
                        continue
                    data.append(nest[k])
                    del nest[k]

                high = get_k_line_column(data=data, depth=20)
                ma_5 = ma(elements=high, step=5)
                ma_10 = ma(elements=high, step=10)
                print              high
                print                ma_5
                print  ma_10
                cu = cross(ma_5, ma_10)
                print  cu
                far = be_apart_from(cu)
                print                far

            print nest

        except Queue.Empty as e:
            pass


if __name__ == "__main__":
    init_data()
    login()
