#encoding:utf-8
import datetime
from function import generate_ohlc_key
import Queue
from datetime import datetime
import time
import decimal

q_bar = Queue.Queue()
nest = dict()
int_instruments = ['rb', 'hc', 'ru', 'ni', 'cu']

def tickToBar(tick, granularity = 180):
    #tick data to bar
    # global bars
    instrument_id = tick.InstrumentID
    action_day = tick.ActionDay
    update_time = tick.UpdateTime.replace(':', '')

    last_price = int(tick.LastPrice) if instrument_id[0:2] in int_instruments else float(tick.LastPrice)

    volume = tick.Volume

    # if volume == 0:
    #     continue

    if update_time.find('.') != -1:
        dt = datetime.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S.%f")
        timestamp = time.mktime(dt.timetuple()) + (dt.microsecond / 1e6)

    else:
        timestamp = int(time.mktime(time.strptime(' '.join([action_day, update_time]), "%Y%m%d %H%M%S")))

    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    ohlc_key = generate_ohlc_key(instrument_id=instrument_id, granularity=granularity, timestamp=timestamp)

    if ohlc_key not in nest:
        nest[ohlc_key] = {
            'date_time': date_time,
            'last_timestamp': timestamp,
            'high': last_price,
            'low': last_price,
            'close': last_price,
            'open': last_price
        }

    nest[ohlc_key]['last_timestamp'] = timestamp
    nest[ohlc_key]['date_time'] = date_time

    nest[ohlc_key]['close'] = last_price

    if last_price > nest[ohlc_key]['high']:
        nest[ohlc_key]['high'] = last_price

    elif last_price < nest[ohlc_key]['low']:
        nest[ohlc_key]['low'] = last_price

    if nest.__len__() > 1:
        for k, v in nest.items():
            if k == ohlc_key:
                continue
            q_bar.put(nest[k])
            del nest[k]

    # print nest
