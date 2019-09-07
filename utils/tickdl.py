#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'


from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader


import getopt,os,sys,re
import json


api = TqApi(TqSim())





inst = 'rb1905'
exchangeid = 'SHFE'
instid = ''.join([exchangeid, '.', inst])

tickfile =inst+'tick.csv'
# interval = 60
stdt = datetime(2016, 1, 1)
eddt = datetime.now()

# 下载从 2018-01-01 到 2018-06-01 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
# 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
# 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
# 下载从 2018-05-01 到 2018-07-01 的 T1809 盘口Tick数据
td = DataDownloader(api, symbol_list=[instid], dur_sec=0,
                    start_dt=stdt, end_dt=eddt, csv_file_name=tickfile)

while not td.is_finished():
    api.wait_update()
    print("progress:  tick:%.2f%%" % td.get_progress())
