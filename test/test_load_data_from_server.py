#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
sys.path.append('../')


from function import load_data_from_server, get_k_line_column


__author__ = 'James Iter'
__date__ = '2018/8/6'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


if __name__ == "__main__":
    data = load_data_from_server(server_base='http://106.14.119.122', instruments_id='rb1810', granularity='3600')
    high = get_k_line_column(data=data, depth=10)
    pass

