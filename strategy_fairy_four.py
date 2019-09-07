#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import threading
from copy import deepcopy
from data_sewing_machine import sewing_data_to_file_and_depositary, incept_config, load_data_from_file
from data_sewing_machine import init_k_line_pump, get_k_line_column, DEPOSITARY_OF_KLINE, q_macs, get_last_k_line
from data_sewing_machine import get_mac
from trading_period import TradingPeriod, EXCHANGE_TRADING_PERIOD

import Queue

if sys.platform == 'win32':
    from ctp_win32 import ApiStruct, MdApi, TraderApi

elif sys.platform == 'linux2':
    from ctp_linux64 import ApiStruct, MdApi, TraderApi


__author__ = 'James Iter'
__date__ = '2018/4/25'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


inst = [u'rb1805']
BROKER_ID = '9999'
INVESTOR_ID = '116667'
PASSWORD = '110.com'
ADDRESS_MD = 'tcp://180.168.146.187:10031'

q_depth_market_data = Queue.Queue()


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
            print "get today's trading day:", repr(self.GetTradingDay())
            self.subscribe_market_data(self.instruments)

    def subscribe_market_data(self, instruments):
        self.SubscribeMarketData(instruments)

    def OnRtnDepthMarketData(self, depth_market_data):
        q_depth_market_data.put(deepcopy(depth_market_data))


def run():
    # 登录行情服务器
    user = MyMdApi(instruments=inst, broker_id=BROKER_ID, investor_id=INVESTOR_ID, password=PASSWORD)
    user.Create("data")
    user.RegisterFront(ADDRESS_MD)
    user.Init()
    print u'行情服务器登录成功'

    last_time = None
    up_trader_flag = False
    down_trader_flag = False

    while True:
        try:
            payload = q_depth_market_data.get(timeout=1)
            sewing_data_to_file_and_depositary(depth_market_data=payload)

            last_k_line = get_last_k_line(instrument_id=inst[0], interval=60)

            if last_k_line is not None:
                if last_time != last_k_line['date_time']:
                    last_time = last_k_line['date_time']
                    up_trader_flag = False
                    down_trader_flag = False

                if not up_trader_flag and payload.LastPrice > last_k_line['high']:
                    # 下多单
                    up_trader_flag = True
                    print
                    print u'下多单'
                    print last_k_line
                    print payload.LastPrice

                if not down_trader_flag and payload.LastPrice < last_k_line['low']:
                    # 下空单
                    down_trader_flag = True
                    print
                    print u'下空单'
                    print last_k_line
                    print payload.LastPrice

                print get_mac(instrument_id='rb1805', interval='120', mac='2c5')

        except Queue.Empty as e:
            pass


def macs_process():
    while True:
        try:
            payload = q_macs.get(timeout=1)
            # print payload

        except Queue.Empty as e:
            pass


if __name__ == "__main__":

    t = threading.Thread(target=macs_process)
    t.setDaemon(False)
    t.start()

    config = incept_config()
    # load_data_from_file()
    load_data_from_file(instruments_id='rb1805,AP810', granularities='1,2,5')
    init_k_line_pump()

    workdays = TradingPeriod.get_workdays(begin=config['begin'], end=config['end'])
    workdays_exchange_trading_period_by_ts = \
        TradingPeriod.get_workdays_exchange_trading_period(
            _workdays=workdays, exchange_trading_period=EXCHANGE_TRADING_PERIOD)

    run()


