#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import json
import traceback
from datetime import datetime
import decimal
import re

from models import Utils
from models import Database as db
from models.initialize import app, logger
from trading_period import TradingPeriod, EXCHANGE_TRADING_PERIOD, FUTURES_TRADING_PERIOD_MAPPING, HOLIDAYS
from function import trading_time_filter


__author__ = 'James Iter'
__date__ = '2018/7/29'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


db.init_conn_redis()

pattern = re.compile(r'\D*')


class DataArrangeEngine(object):
    """
    编排规范

    ============== 数据结构 - OHLC Index ===============
    Key@ Z:合约号_周期
    示例@ Z:rb1801_120

    Value@ timestamp OHLCKey
    示例@ 1508204160 H:rb1801_120:20171017:093600

    ================ 数据结构 - OHLC ===================
    Key@ H:合约号_周期:日期:时间
    示例@ H:rb1801_120:20171017:093600

    Value@ {
        'open': open_NO.,
        'high': high_NO.,
        'low': low_NO.,
        'close': close_NO.,
        'last_timestamp': last_timestamp,
        'date_time': 'human-readable date time'
    }
    示例@ {
        'open': 3449,
        'high': 3449,
        'low': 3447,
        'close': 3447,
        'last_timestamp': 1508204160,
        'date_time': '2017-10-17 09:36:00'
    }
    """

    # rb1801
    instrument_id = None

    # 120 (秒)
    granularity = None

    # 3447
    last_price = None

    # 1508204160
    timestamp = None

    @classmethod
    def generate_ohlc_index_key(cls):
        return ':'.join(['Z', cls.instrument_id + '_' + cls.granularity.__str__()])

    @classmethod
    def generate_ohlc_key(cls):

        remainder = cls.timestamp % cls.granularity

        time_line_timestamp = cls.timestamp

        if remainder:
            time_line_timestamp = cls.timestamp + cls.granularity - remainder

        # 20171017:093600
        time_line = time.strftime("%Y%m%d:%H%M%S", time.localtime(time_line_timestamp))
        return ':'.join(['H', cls.instrument_id + '_' + cls.granularity.__str__(), time_line])

    @classmethod
    def generate_ohlc_index(cls):
        key = cls.generate_ohlc_index_key()
        score = cls.timestamp
        value = cls.generate_ohlc_key()

        # 可重入，不会产生副作用
        # http://redisdoc.com/sorted_set/zadd.html
        db.r.zadd(key, score, value)

    @classmethod
    def set_ohlc(cls):
        ohlc_key = cls.generate_ohlc_key()
        ohlc = db.r.hgetall(ohlc_key)

        # 2017-10-17 09:36:00
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cls.timestamp))

        # 如果 ohlc 为空，即空字典 --> {}
        if not ohlc:
            ohlc = {
                'open': cls.last_price,
                'high': cls.last_price,
                'low': cls.last_price,
                'close': cls.last_price,
                'last_timestamp': cls.timestamp,
                'date_time': date_time
            }

            db.r.hmset(ohlc_key, ohlc)
            return

        if cls.timestamp <= decimal.Decimal(ohlc['last_timestamp']):
            return

        ohlc['last_timestamp'] = cls.timestamp
        ohlc['date_time'] = date_time

        ohlc['close'] = cls.last_price

        if cls.last_price > decimal.Decimal(ohlc['high']):
            ohlc['high'] = cls.last_price

        elif cls.last_price < decimal.Decimal(ohlc['low']):
            ohlc['low'] = cls.last_price

        db.r.hmset(ohlc_key, ohlc)

        if cls.granularity == 60:
            ohlc['instrument_id'] = cls.instrument_id
            db.r.publish('PS:MinuteKLine', message=json.dumps(ohlc))

    @classmethod
    def data_arrange(cls, awp_tick=None):
        """
        数据编排
        :param awp_tick: {
            'granularities': [60, 120, 300, 600, 1800],
            'instrument_id': 'rb1801',
            'last_price': 3447,
            'action_day': '20171017',
            'update_time': '093600'
        }
        :return:
        """

        if not isinstance(awp_tick, dict):
            log = u' '.join([u'数据 --> ', str(awp_tick), u' 需为 json 格式'])
            logger.warning(msg=log)
            return

        if 'granularities' not in awp_tick or not isinstance(awp_tick['granularities'], list):
            log = u'granularities 需为 list 格式'
            logger.warning(msg=log)
            return

        action_day = awp_tick['action_day']
        update_time = awp_tick['update_time']

        cls.instrument_id = awp_tick['instrument_id']
        cls.last_price = awp_tick['last_price']

        if update_time.find('.') != -1:
            dt = datetime.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S.%f")
            cls.timestamp = time.mktime(dt.timetuple()) + (dt.microsecond / 1e6)

        else:
            cls.timestamp = int(time.mktime(time.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S")))

        for granularity in awp_tick['granularities']:
            cls.granularity = granularity
            cls.generate_ohlc_index()
            cls.set_ohlc()

    @classmethod
    def launch(cls):
        workdays = TradingPeriod.get_workdays(begin='2016-12-31', end='2018-10-07')
        workdays_exchange_trading_period_by_ts = \
            TradingPeriod.get_workdays_exchange_trading_period(
                _workdays=workdays, exchange_trading_period=EXCHANGE_TRADING_PERIOD)

        while True:
            if Utils.exit_flag:
                msg = 'Thread DataArrangeEngine say bye-bye'
                print msg
                logger.info(msg=msg)

                return

            try:
                awp_tick = db.r.lpop(app.config['data_stream_queue'])

                if awp_tick is None:
                    time.sleep(1)
                    continue

                awp_tick = json.loads(awp_tick)

                # 过滤交易量为 0 的假数据
                if 'volume' in awp_tick and awp_tick['volume'] == 0:
                    continue

                contract_code = pattern.match(awp_tick['instrument_id']).group()
                action_day = awp_tick['action_day']
                update_time = awp_tick['update_time']
                # 时间合法性校验
                if not trading_time_filter(
                        date_time=' '.join([action_day, update_time]), contract_code=contract_code,
                        exchange_trading_period_by_ts=workdays_exchange_trading_period_by_ts[
                            '-'.join([action_day[:4], action_day[4:6], action_day[6:]])]):
                    continue

                cls.data_arrange(awp_tick=awp_tick)

            except AttributeError as e:
                logger.error(traceback.format_exc())
                time.sleep(1)

                if db.r is None:
                    db.init_conn_redis()

            except Exception as e:
                logger.error(traceback.format_exc())
                time.sleep(1)


if __name__ == '__main__':
    try:
        DataArrangeEngine.launch()

    except:
        logger.error(traceback.format_exc())
        exit(-1)
