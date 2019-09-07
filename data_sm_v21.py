#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this is for pypy

import Queue

from utils.vtObject import VtTickData


from models import Utils
from models.initialize import logger
from function import load_data_from_server, get_k_line_column, ma, cross, be_apart_from


from ctp.futures import ApiStruct, MdApi, TraderApi
from getaccount import getAccountinfo
from tickToBar import tickToBar, q_bar

BROKER_ID, INVESTOR_ID, PASSWORD, ADDRESS_MD, ADDRESS_TD = getAccountinfo('simnow24_ctp.json')
 

__author__ = 'James Iter'
__date__ = '2018/8/27'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


q_depth_market_data = Queue.Queue()

granularity = 180

inst = [u'rb1901']

def init_data():
    global data

    # for interval in granularity:

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
        tick = VtTickData()
        tick.InstrumentID = depth_market_data.InstrumentID
        tick.LastPrice = depth_market_data.LastPrice
        tick.UpdateTime = depth_market_data.UpdateTime
        tick.ActionDay = depth_market_data.ActionDay
        tick.Volume = depth_market_data.Volume

        q_depth_market_data.put(tick)

        # q_depth_market_data.put(depth_market_data)


def login():
    # 登录行情服务器
    user = MyMdApi(instruments=inst, broker_id=BROKER_ID, investor_id=INVESTOR_ID, password=PASSWORD)
    user.Create("data")
    user.RegisterFront(ADDRESS_MD)
    user.Init()

    print u'行情服务器登录成功'

    bars = load_data_from_server(server_base='http://106.14.119.122', instruments_id=inst[0], granularity=granularity)

    while True:

        if Utils.exit_flag:
            msg = 'Thread CTPDataCollectEngine say bye-bye'
            print msg
            logger.info(msg=msg)

            return

        try:
            payload = q_depth_market_data.get(timeout=1)
            q_depth_market_data.task_done()

            instrument_id = payload.InstrumentID
            action_day = payload.ActionDay
            update_time = payload.UpdateTime.replace(':', '')
            last_price = payload.LastPrice
            volume = payload.Volume

            if volume == 0:
                continue


            tickToBar(payload, 13)


            if not q_bar.empty():
                bar = q_bar.get()
                bars.append(bar)
                high = get_k_line_column(data=bars, depth=20)
                low = get_k_line_column(data=bars, ohlc='low')

                ma_5 = ma(elements=high, step=5)
                ma_10 = ma(elements=high, step=10)
                print high
                print ma_5
                print ma_10
                cu = cross(ma_5, ma_10)
                print cu
                far = be_apart_from(cu)
                print far



        except Queue.Empty as e:
            pass


if __name__ == "__main__":

    # init_data()
    login()

