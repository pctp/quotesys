#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import json
import requests

from datetime import datetime
import time

from trading_period import TradingPeriod, EXCHANGE_TRADING_PERIOD, FUTURES_TRADING_PERIOD_MAPPING, HOLIDAYS


__author__ = 'James Iter'
__date__ = '2018/5/13'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


def load_data_from_file(instruments_id=None, granularities=None, data_source_dir='./'):

    ret = dict()
    files_name = list()
    instrument_id_interval_pattern = re.compile(r'(\D*\d+)_(\d+)\.json')

    if instruments_id is not None and granularities is not None:
        for instrument_id in instruments_id.split(','):
            for granularity in granularities.replace(' ', '').split(','):

                file_name = '_'.join([instrument_id, granularity]) + '.json'

                files_name.append(file_name)

    else:
        for file_name in os.listdir(data_source_dir):
            files_name.append(file_name)

    for file_name in files_name:
        p = instrument_id_interval_pattern.match(file_name)

        if p is not None:
            fields = p.groups()
            key = '_'.join([fields[0], fields[1]])

            if key not in ret:
                ret[key] = list()

    for k, v in ret.items():
        file_path = os.path.join(data_source_dir, k + '.json')

        if not os.path.isfile(file_path):
            continue

        with open(file_path, 'r') as f:
            for line in f:
                json_k_line = json.loads(line.strip())
                ret[k].append(json_k_line)

    return ret


def load_data_from_server(server_base='http://127.0.0.1', instruments_id=None, granularity=None):
    url = server_base + '/api/ohlc/' + instruments_id.__str__() + '/' + granularity.__str__()
    r = requests.get(url)
    j_r = json.loads(r.content)
    bars = j_r['data']
    for j in bars:
        j[u'open'] = float(j[u'open'])
        j[u'high'] = float(j[u'high'])
        j[u'low'] = float(j[u'low'])
        j[u'close'] = float(j[u'close'])

    return bars


def get_k_line_column(data=None, ohlc='high', depth=0):
    """
    :param data: 数据源
    :param ohlc: [Open|High|Low|Close]。
    :param depth: 深度。默认 0 将获取所有。
    :return: list。
    """

    ohlc = ohlc.lower()

    assert ohlc in ['open', 'high', 'low', 'close']

    ret = list()
    max_depth = data.__len__()
    if depth == 0 or depth >= max_depth:
        depth = max_depth

    depth = 0 - depth

    for i in range(depth, 0):
        ret.append((data[i][ohlc], data[i]['date_time']))

    return ret


def get_last_k_line(data=None):
    """
    :param data: 数据源
    :return: dict。
    """

    if 1 > data.__len__():
        return None

    return data[-1]


def trading_time_filter(date_time=None, contract_code=None, exchange_trading_period_by_ts=None):
    is_tick = False
    if date_time.find('.') != -1:
        is_tick = True

    if is_tick:
        dt = datetime.strptime(date_time, "%Y%m%d %H%M%S.%f")
        ts = time.mktime(dt.timetuple()) + (dt.microsecond / 1e6)
    else:
        ts = int(time.mktime(time.strptime(date_time, "%Y%m%d %H%M%S")))

    contract_trading_period_ts = list()

    for trading_period in FUTURES_TRADING_PERIOD_MAPPING[contract_code]:
        if trading_period.exchange_code not in exchange_trading_period_by_ts:
            continue

        if trading_period.period not in exchange_trading_period_by_ts[trading_period.exchange_code]:
            continue

        contract_trading_period_ts.extend(
            exchange_trading_period_by_ts[trading_period.exchange_code][trading_period.period])

    for trading_period_ts in contract_trading_period_ts:
        if trading_period_ts[0] <= ts <= trading_period_ts[1]:
            return True

    return False


def generate_ohlc_key(instrument_id=None, granularity=None, timestamp=None):

    remainder = timestamp % granularity

    time_line_timestamp = timestamp

    if remainder:
        time_line_timestamp = timestamp + granularity - remainder

    # 20171017:093600
    time_line = time.strftime("%Y%m%d:%H%M%S", time.localtime(time_line_timestamp))
    return ':'.join(['H', instrument_id + '_' + granularity.__str__(), time_line])


def ma(elements=None, step=None):
    assert isinstance(elements, list)
    assert isinstance(step, int)

    import decimal

    numbers = list()
    ma_list = list()

    for ele in elements:
        numbers.append(decimal.Decimal(ele))

        if numbers.__len__() < step:
            avg = float('%0.2f' % (float(sum(numbers)) / numbers.__len__()))

        else:
            numbers = numbers[0 - step:]
            avg = float('%0.2f' % (float(sum(numbers)) / numbers.__len__()))

        ma_list.append(avg)

    return ma_list


def cross(series_a=None, series_b=None):

    assert isinstance(series_a, list)
    assert isinstance(series_b, list)
    assert series_a.__len__() == series_b.__len__()

    cross_series = list()

    for i, v in enumerate(series_a):
        if i > 0:
            if series_a[i] > series_b[i] and series_a[i - 1] <= series_b[i - 1]:
                cross_series.append(True)
                continue

        cross_series.append(None)

    return cross_series


def be_apart_from(series):
    assert isinstance(series, list)
    assert series.__len__() > 0

    i = series.__len__() - 1

    while i >= 0:

        if series[i] is True:
            return series.__len__() - i

        i -= 1

    return None


