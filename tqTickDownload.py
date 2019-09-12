#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'


from datetime import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader

import getopt,os,sys,re

import json


def incept_config():
    config = {'output_dir': os.getcwd()}

    pattern = re.compile(r'\D*')

    def usage():
        print(("Usage:%s [-s] [--data_source]" % sys.argv[0]))
        print("-s --InstrumentID, Must include exchange ID., ex: SHFE.rb2001")
        print("-o --output_dir, is the output directory. optional.")

    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:o:n:',
                                   ['help', 'data_source=', 'output_dir='])
    except getopt.GetoptError as e:
        print()
        str(e)
        usage()
        exit(e.message.__len__())

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            exit()

        elif k in ("-s", "--data_source"):
            config['data_source'] = v

        elif k in ("-o", "--output_dir"):
            config['output_dir'] = v

        else:
            print()
            "unhandled option"

    if 'data_source' not in config:
        print()
        'Must specify the -s(data_source) arguments.'
        usage()
        exit(1)

    if 'name' not in config:
        config['name'] = os.path.basename(config['data_source']).split('.')[0]

    return config





config = incept_config()
instid= config['data_source']


def isinstidValid(instid):
    exchanges = ['CZCE', 'DCE', 'SHFE', 'CEFFEX']
    for exchangeid in exchanges:
        if exchangeid not in instid:
            continue
        else:
            return True

    return False

print((isinstidValid(instid)))


def main():

    api = TqApi(TqSim())
    inst = instid.split('.')[1]
    tickfile =inst+'tick.csv'
    stdt = datetime(2016, 1, 1)
    eddt = datetime.now()
    # eddt = datetime(2018, 8, 30)
    # 下载从 2018-01-01 到 2018-06-01 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
    # 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
    # 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
    # 下载从 2018-05-01 到 2018-07-01 的 T1809 盘口Tick数据
    td = DataDownloader(api, symbol_list=[instid], dur_sec=0,
                        start_dt=stdt, end_dt=eddt, csv_file_name=tickfile)
    with closing(api):
    	while not td.is_finished():
        	api.wait_update()
        	print(("progress:  tick:%.2f%%" % td.get_progress()))


if __name__ == "__main__":
    # pass
    main()
