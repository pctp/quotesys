#!/usr/bin/env python
# -*- coding: utf-8 -*-


import getopt
import sys
import os
import json

from models import Database as db


__author__ = 'James Iter'
__date__ = '2018-12-06'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


def incept_config():
    config = {
        'interval': '2'
    }

    def usage():
        print "Usage:%s [-s] [--data_source]" % sys.argv[0]
        print "-o --output_file, is the output file. optional."
        print "-i --interval, default is 2 minutes, delimiter is a comma. optional."

    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ho:i:',
                                   ['help', 'output_file=', 'interval='])
    except getopt.GetoptError as e:
        print str(e)
        usage()
        exit(e.message.__len__())

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            exit()

        elif k in ("-o", "--output_file"):
            config['output_dir'] = v

        elif k in ("-i", "--interval"):
            config['interval'] = v

        else:
            print "unhandled option"

    if 'output_file' not in config:
        config['output_file'] = '_'.join([os.path.basename(
            config['data_source']).split('.')[0], config['interval']]) + '.json'

    config['interval'] = int(config['interval'])

    return config


def run():
    config = incept_config()

    save_path = os.path.join(os.getcwd(), config['output_file'])

    if not os.path.isdir(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path), 0755)

    i = 0
    k_line = None

    while True:

        ps = db.r.pubsub(ignore_subscribe_messages=False)
        ps.subscribe('PS:MinuteKLine')

        last_k_line = ps.get_message(timeout=1)

        if last_k_line is None or not isinstance(last_k_line, basestring):
            continue

        try:
            last_k_line = json.loads(last_k_line)

        except ValueError as e:
            continue

        i += 1

        if k_line is None:
            k_line = last_k_line

        if i % config['interval'] == 0:
            k_line = last_k_line

            with open(save_path, 'a') as f2:
                f2.writelines(json.dumps(k_line, ensure_ascii=False) + '\n')

        else:
            k_line['date_time'] = last_k_line['date_time']
            k_line['close'] = last_k_line['close']

            if last_k_line['high'] > k_line['high']:
                k_line['high'] = last_k_line['high']

            elif last_k_line['low'] < k_line['low']:
                k_line['low'] = last_k_line['low']

            else:
                pass

    pass


if __name__ == '__main__':
    run()
