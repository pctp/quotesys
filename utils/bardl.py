#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'

from datetime import datetime

# from tqsdk.tools.downloader import DataDownloader


from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader
import getopt,os,sys,re

api = TqApi(TqSim())


# url = 'ws://192.168.1.20:7777'
# api = TqApi("SIM",url)

# 下载从 2018-01-01 到 2018-06-01 的 cu1805,cu1807,IC1803 分钟线数据，所有数据按 cu1805 的时间对齐
# 例如 cu1805 夜盘交易时段, IC1803 的各项数据为 N/A
# 例如 cu1805 13:00-13:30 不交易, 因此 IC1803 在 13:00-13:30 之间的K线数据会被跳过
#

def incept_config():
    config = {
        'output_dir': os.getcwd()
        }

    pattern = re.compile(r'\D*')

    def usage():
        print("Usage:%s [-s] [--data_source]" % sys.argv[0])
        # print "-s --data_source, is the path of data file."
        print("-o --output_dir, is the output directory. optional.")
        print("-n --name, is the instrument id. optional.")
        print("-g --granularities, default are 2,5,10,30,60 minutes, delimiter is a comma. optional.")
        print("-b --begin, default is HOLIDAYS first element, format is YYYY-MM-DD. optional.")
        print("-e --end, default is today, format is YYYY-MM-DD. optional.")
        print("-t --offset, default is 0, unit is second. optional.")

    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:o:n:g:b:e:t:',
                                   ['help', 'data_source=', 'output_dir=', 'name=', 'granularities=', 'begin=', 'end=',
                                    'offset='])
    except getopt.GetoptError as e:
        print(str(e))
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

        elif k in ("-n", "--name"):
            config['name'] = v

        elif k in ("-g", "--granularities"):
            config['granularities'] = v

        elif k in ("-b", "--begin"):
            config['begin'] = v

        elif k in ("-e", "--end"):
            config['end'] = v

        elif k in ("-t", "--offset"):
            config['offset'] = int(v)

        else:
            print("unhandled option")




    #
    # if 'end' not in config:
    #     config['end'] = time.strftime('%Y-%m-%d')
    #
    # if 'offset' not in config:
    #     config['offset'] = 0

    return config



# instrumentid = "KQ.i@SHFE.rb"
# klinefile ='rb0000.csv'

def run(instrumentid, period, exchangeId = 'SHFE'):
    inst = instrumentid
    exchangeid = exchangeId
    period = int(period) if period is not None else 780

    instid = ''.join([exchangeid, '.', inst])
    datafile =inst+'_'+str(period)+'.csv'
    enddt = datetime.now()
    kd = DataDownloader(api, symbol_list=[instid], dur_sec=period,
                    start_dt=datetime(2016, 1, 1), end_dt=enddt, csv_file_name=datafile)

    with closing(api):

	    while not kd.is_finished():
	        api.wait_update()
	        print("progress: kline: %.2f%%" % kd.get_progress())



config = incept_config()
print(config['name'], config['granularities'])

run(instrumentid=config['name'], period=config['granularities'])

