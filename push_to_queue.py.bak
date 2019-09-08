#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import getopt
import json
import time

from models import Database as db
from models.initialize import app, logger


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


db.init_conn_redis()


def incept_config():
    config = {
        'granularities': '120,300,600,1800,3600'
    }

    def usage():
        print "Usage:%s [-s] [--data_source]" % sys.argv[0]
        print "-s --data_source, is the path of data file."
        print "-n --name, is the instrument id. optional."
        print "-g --granularities, default are 120,300,600,1800,3600 minutes, delimiter is a comma. optional."

    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:n:g:',
                                   ['help', 'data_source=', 'name=', 'granularities='])
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

        elif k in ("-n", "--name"):
            config['name'] = v

        elif k in ("-g", "--granularities"):
            config['granularities'] = v

        else:
            print "unhandled option"

    if 'data_source' not in config:
        print 'Must specify the -s(data_source) arguments.'
        usage()
        exit(1)

    if 'name' not in config:
        config['name'] = os.path.basename(config['data_source']).split('.')[0]

    config['instrument_id'] = config['name']

    for granularity in config['granularities'].split(','):

        if not isinstance(config['granularities'], list):
            config['granularities'] = list()

        # 忽略非整数的粒度
        if not granularity.isdigit():
            continue

        else:
            granularity = int(granularity)

        # 粒度小于 2 分钟，或大于 60 分钟的不予支持
        if 120 > granularity > 3600:
            continue

        config['granularities'].append(granularity)

    return config


def run():
    config = incept_config()
    config['is_tick'] = None
    lines = list()

    with open(config['data_source']) as f:
        for i, line in enumerate(f):

            # 忽略 csv 头
            if i == 0:
                continue

            lines.append(line)

    for i, line in enumerate(lines):

        if i % 10000 == 0:
            print ' '.join([time.strftime('%H:%M:%S'), i.__str__()])

        awp_tick = {
            'instrument_id': config['instrument_id'],
            'granularities': config['granularities']
        }

        row = line.split(',')

        row[0] = row[0].replace('/', '-')

        if config['is_tick'] is None:
            if row[0].find('.') != -1:
                config['is_tick'] = True

            else:
                config['is_tick'] = False

        date_time = row[0].split(' ')

        awp_tick['action_day'] = date_time[0].replace('-', '')
        awp_tick['update_time'] = date_time[1].replace(':', '')

        if config['is_tick']:
            awp_tick['last_price'] = row[1]

        else:
            awp_tick['last_price'] = row[4]

        if awp_tick['last_price'].isdigit():
            awp_tick['last_price'] = int(awp_tick['last_price'])

        else:
            try:
                awp_tick['last_price'] = float('%0.2f' % float(awp_tick['last_price']))

            except ValueError:
                continue

        db.r.rpush(app.config['data_stream_queue'], json.dumps(awp_tick, ensure_ascii=False))


if __name__ == '__main__':
    run()

