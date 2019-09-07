#!/usr/bin/env python
# -*- coding: utf-8 -*-


from decimal import Decimal
from models import Database as db
from models import OHLCIndex


__author__ = 'James Iter'
__date__ = '2018/8/1'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


class OHLC(object):

    def __init__(self, contract_code=None, granularity=None, **kwargs):
        self.contract_code = contract_code
        self.granularity = granularity
        self.start = kwargs.get('start', 0)
        self.end = kwargs.get('end', None)
        self._min = kwargs.get('_min', 0)
        self._max = kwargs.get('_max', None)
        self.ohlc_rows = None
        self.ohlc_index = OHLCIndex(contract_code=self.contract_code, granularity=self.granularity)

        if self._max is not None and self.end is not None:
            self.ohlc_keys = self.ohlc_index.get_by_score_range(
                _min=self._min, _max=self._max, start=self.start, end=self.end)

        elif self._max is not None:
            self.ohlc_keys = self.ohlc_index.get_by_score(_min=self._min, _max=self._max)

        elif self.end is not None:
            self.ohlc_keys = self.ohlc_index.get_by_range(start=self.start, end=self.end)

        else:
            self.end = -1
            self.ohlc_keys = self.ohlc_index.get_by_range(start=self.start, end=self.end)

        self.ohlc_rows = self.get_by_ohlc_keys()

    def get_by_ohlc_keys(self):

        with db.r.pipeline() as pipe:
            for ohlc_key in self.ohlc_keys:
                pipe.hgetall(ohlc_key)

            return pipe.execute()

    def get_column(self, ohlc='high', depth=0):
        ohlc = ohlc.lower()

        assert ohlc in ['open', 'high', 'low', 'close']
        column = list()
        max_depth = self.ohlc_rows.__len__()
        if depth == 0 or depth >= max_depth:
            depth = max_depth

        depth = 0 - depth

        for i in range(depth, 0):
            column.append(self.ohlc_rows[i][ohlc])

        return column

    def hhv(self, depth=0, step=None):

        if depth < 1:
            assert 0 < step <= self.ohlc_rows.__len__()

        else:
            assert 0 < step <= depth

        numbers = list()
        stack = list()

        for number in self.get_column(ohlc='high', depth=depth):
            stack.append(number)

            if stack.__len__() > step:
                stack = stack[0 - step:]

            numbers.append(max(stack))

        return numbers

    def llv(self, depth=0, step=None):

        if depth < 1:
            assert 0 < step <= self.ohlc_rows.__len__()

        else:
            assert 0 < step <= depth

        numbers = list()
        stack = list()

        for number in self.get_column(ohlc='low', depth=depth):
            stack.append(number)

            if stack.__len__() > step:
                stack = stack[0 - step:]

            numbers.append(min(stack))

        return numbers

    @staticmethod
    def cross_up(series_a=None, series_b=None):

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

    @staticmethod
    def cross_down(series_a=None, series_b=None):

        assert isinstance(series_a, list)
        assert isinstance(series_b, list)
        assert series_a.__len__() == series_b.__len__()

        cross_series = list()

        for i, v in enumerate(series_a):
            if i > 0:
                if series_a[i] < series_b[i] and series_a[i - 1] >= series_b[i - 1]:
                    cross_series.append(True)
                    continue

            cross_series.append(None)

        return cross_series

    def rsv(self, n=0):

        if n == 0:
            n = self.ohlc_rows.__len__()

        close = Decimal(self.ohlc_rows[-1]['close'])
        llv_n = Decimal(self.llv(depth=n, step=n)[-1])
        hhv_n = Decimal(self.hhv(depth=n, step=n)[-1])

        ret = {
            'ohlc_rows': self.ohlc_rows,
            'close': float('%0.2f' % float(close)),
            'llv_n': float('%0.2f' % float(llv_n)),
            'hhv_n': float('%0.2f' % float(hhv_n)),
            'rsv': float('%0.2f' % float((close - llv_n) / (hhv_n - llv_n) * 100))
        }

        return ret

