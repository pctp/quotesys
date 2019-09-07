#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json


__author__ = 'James Iter'
__date__ = '2018/8/2'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


def data_to_file():
    url = 'http://106.14.119.122/api/ohlc/rb1810/120'
    r = requests.get(url)
    j_r = json.loads(r.content)

    with open('file_path', 'a') as f:
        for item in j_r['data']:
            f.writelines(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == "__main__":
    data_to_file()

