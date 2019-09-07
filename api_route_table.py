#!/usr/bin/env python
# -*- coding: utf-8 -*-


from models.utils import add_rule_api
from api import ohlc


__author__ = 'James Iter'
__date__ = '2018/08/01'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2018 by James Iter.'


# OHLC
add_rule_api(ohlc.blueprint, '/<contract_code>/<granularity>', api_func='ohlc.r_get', methods=['GET'])
add_rule_api(ohlc.blueprint, '/<contract_code>/<granularity>/<start>/<end>',
             api_func='ohlc.r_get_by_range', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_by_score/<contract_code>/<granularity>/<_min>/<_max>',
             api_func='ohlc.r_get_by_score', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_hhv/<contract_code>/<granularity>/<start>/<end>/<step>',
             api_func='ohlc.r_hhv_by_range', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_llv/<contract_code>/<granularity>/<start>/<end>/<step>',
             api_func='ohlc.r_llv_by_range', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_hhv_llv_cross_up_by_range/<contract_code>/<granularity>/<start>/<end>/<steps>',
             api_func='ohlc.r_hhv_llv_cross_up_by_range', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_hhv_llv_cross_down_by_range/<contract_code>/<granularity>/<start>/<end>/<steps>',
             api_func='ohlc.r_hhv_llv_cross_down_by_range', methods=['GET'])

add_rule_api(ohlc.blueprint, '/_rsv/<contract_code>/<granularity>/<n>',
             api_func='ohlc.r_rsv', methods=['GET'])
