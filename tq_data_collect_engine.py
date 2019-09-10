#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from copy import deepcopy
import queue
import json

from models import Utils
from models import Database as db
from models.initialize import app, logger


__author__ = 'James Iter, smartmanp, smartmanp@qq.com'
__date__ = '2018/4/22, 2019/09/10'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


db.init_conn_redis()


inst = ['AP810', 'rb1810']

q_depth_market_data = queue.Queue()

granularities = [60, 120, 300, 600,900, 1800]

from tqsdk import TqApi, TqAccount
acc=TqAccount(100000)
api=TqApi(acc)
quotes ={}

for i in inst:
	quote[i]=api.get_quote(i)






def login():

   

    print('行情服务器登录成功')

    while True:

    	api.wait_update()

    	if api.ischange():
    		pass
    		 

        if Utils.exit_flag:
            msg = 'Thread CTPDataCollectEngine say bye-bye'
            print(msg)
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

            print(awp_tick)
            # db.r.rpush(app.config['data_stream_queue'], json.dumps(awp_tick, ensure_ascii=False))

        except queue.Empty as e:
            pass


if __name__ == "__main__":

    login()


