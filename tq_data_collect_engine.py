#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'James Iter, smartmanp, smartmanp@qq.com'
__date__ = '2018/4/22, 2019/09/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'

import sys
from copy import deepcopy
import queue
import json
from pprint import pprint

from models import Utils
from models import Database as db
from models.initialize import app, logger
from tqsdk import TqApi, TqSim, TqAccount, TargetPosTask, TqBacktest
from dataclasses import dataclass

@dataclass
class tickdata():
    InstrumentID: str
    LastPrice: float
    ActionDay: str
    UpdateTime: str
    Volume: int


acc = TqSim(150000)
api = TqApi(acc)

db.init_conn_redis()

inst = ['CZCE.SR001', 'SHFE.rb2001','DCE.pp2001']

q_depth_market_data = queue.Queue()

granularities = [60, 120, 300, 600, 900, 1800]

quotes = {}


for i in inst:
    quotes[i] = api.get_quote(i)

while True:
    api.wait_update()
    for q in quotes:
        if api.is_changing(quotes[q]):
            tick = quotes[q]
            pprint(tick)
            print(tick.datetime, tick.volume, tick.last_price,tick._path[1])



            InstrumentID = q.split('.')[1]
            ActionDay = tick.datetime.split(' ')[0].replace('-', '')
            UpdateTime = tick.datetime.split(' ')[1]
            LastPrice = tick.last_price
            Volume = tick.volume
            # newtick = tickdata(LastPrice=LastPrice, Volume=Volume, UpdateTime= UpdateTime, ActionDay= ActionDay,InstrumentID=InstrumentID)

            awp_tick = {
                'granularities': granularities,
                'instrument_id': InstrumentID,
                'last_price': LastPrice,
                'action_day': ActionDay,
                'update_time': UpdateTime.replace(':', ''),
                'volume': Volume
            }

            print(awp_tick)
            db.r.rpush(app.config['data_stream_queue'], json.dumps(awp_tick, ensure_ascii=False))
            # q_depth_market_data.put(newtick)

            # print(type(quotenow))
            # print(quotenow['datetme'])

