#encoding:utf-8
# from __future__ import print_function
#天勤tick数据清洗：交易时间外的数据清除，时间格式转换为tb格式
#目前版本针对螺纹合约()

import json
from datetime import datetime, timedelta, time
import getopt
import sys
import os
import re

def incept_config():
    config = {'output_dir': os.getcwd()}

    pattern = re.compile(r'\D*')

    def usage():
        print "Usage:%s [-s] [--data_source]" % sys.argv[0]
        print "-s --data_source, is the path of data file."
        print "-o --output_dir, is the output directory. optional."
        
    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:o:n:',
                                   ['help', 'data_source=', 'output_dir='])
    except getopt.GetoptError as e:
        print str(e)
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
            print "unhandled option"

    if 'data_source' not in config:
        print 'Must specify the -s(data_source) arguments.'
        usage()
        exit(1)

    if 'name' not in config:
        config['name'] = os.path.basename(config['data_source']).split('.')[0]


    return config



# 这里以商品期货为例
MORNING_START = time(9, 0)
MORNING_REST = time(10, 15)
MORNING_RESTART = time(10, 30)
MORNING_END = time(11, 30)
AFTERNOON_START = time(13, 30)
AFTERNOON_END = time(15, 0)
NIGHT_START = time(21, 0)
NIGHT_END = time(23, 0)
#针对夜盘23：00结束的；情况，对0点以后的品种目前未考虑。
#考虑针对具体合约进行处理
# NIGHT_END = time(2, 30)

config = incept_config()

filetoclean= config['data_source']

outfile =filetoclean.split('.')[0]+'cleaned.'+filetoclean.split('.')[1]

#String to Date(datetime)
def stringToDate(string):
    #example '2013-07-22 09:44:15+00:00'
    dt = datetime.strptime(string, "%H:%M:%S")
    # print dt
    return dt
#
# def stringToTime(string):
#     #example '09:44:15'
#     dt = datetime.time.strptime(string, "%H:%M:%S")
#     print dt
#     return dt

# #Date(datetime) to String
# def dateToString(date):
#     ds = date.strftime('%Y-%m-%d %H:%M:%S')
#     return ds
# #return n hours after datetime
# def getAfterDate(n):
#     dnow = datetime.datetime.now()
#     dafter = dnow + datetime.timedelta(hours=n)
#     dafter.ctime()
#     return dafter

'''
作者：短腿熊先森 
来源：CSDN 
原文：https://blog.csdn.net/qq_23286071/article/details/79558719 
版权声明：本文为博主原创文章，转载请附上博文链接！
'''





outf = open(outfile,'a')

with open(filetoclean) as f:
    for i, line in enumerate(f):

        # 忽略 csv 头
        if i == 0:
            continue
        # date_time, tlastPrice, tbidPrice1, taskPrice1, tvolume, topenInt ,t1,t2, t3,t4,t5,t6,t7= line.split(',')



        row = line.split(',')
        if 'nan' in row:
            continue

        date_time = row[0]
        dt = stringToDate(date_time.split(' ')[1].split('.')[0]).time()
        # dt = stringToDate(row[0].split(' ')[1]).time()

        ddate = row[0].split()[0]
        dtime = row[0].split()[1][0:12]
        # dttime =row[0].split()[1][0:8]
        # dt = stringToDate(dttime).split()[1].time()

        '''
        if (MORNING_START <= dt < MORNING_REST):
            print dt,u'上午第一段.'
        elif (MORNING_RESTART <= dt < MORNING_END):
            print dt,u'上午第二段.'
        elif(AFTERNOON_START <= dt < AFTERNOON_END):
            print dt,u'下午段'
        elif (dt >= NIGHT_START and dt < NIGHT_END):
            print dt,u'夜盘时间'
        else:
            print dt,u'非交易时间段.'

        '''




        # 如果在交易事件内，则为有效数据， 输出到清洗后的文件中。

        if ((MORNING_START <= dt < MORNING_REST) or
                (MORNING_RESTART <= dt < MORNING_END) or
                (AFTERNOON_START <= dt < AFTERNOON_END) or
                (dt >= NIGHT_START) and (dt < NIGHT_END)):

            # outf.write(line)
            # print(len(row))

            try:
                newrow = ''.join(
                    [ddate, ' ', dtime, ',', row[1], ',', row[2], ',', row[3], ',', row[4], ',', row[5], ',', row[6], ',',
                     row[7], ',', row[8], ',', row[9], ',', row[10]])
                outf.write(newrow)
                continue
            except SyntaxError:
                print SyntaxError
                pass

        else:
            print(dt)

outf.close()
'''
datetime,SHFE.rb1905.last_price,SHFE.rb1905.bid_price1,SHFE.rb1905.ask_price1,SHFE.rb1905.volume,SHFE.rb1905.open_interest
2018-05-15 18:35:32,nan,nan,nan,0,0
2018-05-15 20:59:00,3420.0,3400.0,3420.0,4,4
2018-05-15 21:00:00,3420.0,3402.0,3425.0,10,10
2018-05-15 21:00:01,3425.0,3420.0,3425.0,12,12
2018-05-15 21:00:01,3425.0,3422.0,3425.0,12,12
2018-05-15 21:00:04,3425.0,3422.0,3425.0,14,14
2018-05-15 21:00:05,3425.0,3422.0,3425.0,14,14
2018-05-15 21:00:06,3425.0,3422.0,3424.0,14,14
2018-05-15 21:00:08,3424.0,3422.0,3424.0,16,14
2018-05-15 21:00:13,3424.0,3422.0,3425.0,18,14
2018-05-15 21:00:13,3424.0,3422.0,3424.0,20,16
2018-05-15 21:00:14,3424.0,3423.0,3424.0,20,16
2018-05-15 21:00:14,3425.0,3425.0,3430.0,30,26
2018-05-15 21:00:17,3425.0,3425.0,3430.0,30,26
2018-05-15 21:00:18,3425.0,3425.0,3430.0,30,26
2018-05-15 21:00:20,3430.0,3425.0,3430.0,32,28
2018-05-15 21:00:20,3430.0,3425.0,3430.0,42,38
'''