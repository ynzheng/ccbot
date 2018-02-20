#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import time
import asyncio
import ccxt.async as ccxt
import json
import signal
import functools
from symarbit import get_strtime

g_use_python3 = (sys.version_info[0] == 3)

'''
    def request(self, path, api='public', method='GET',
                params={}, headers=None, body=None):
        pass
'''

'''
季度价格 - 当周价格。大于200美金时候，卖出(做空)季度合约，买入(做多)当周合约。

季度价格 - 当周价格，小于负五十的时候。卖空现货，买入季度。

平仓条件的话。第一个条件时候。既季度价格~当周价格小于150美金以内。第二个则是，季度价格~当周价格大于5美金。

季度价格是在当周价格基础上进行波动。咱们把他分为-60至正数250美金。大部分时候是在50-150区间。每天每时每刻都在波动，但走到区域两边，他价差终究是要回归中间区间。

季度价格是在当周价格基础上进行波动。咱们把他分为-60至正数250美金。大部分时候是在50-150区间。每天每时每刻都在波动，但走到区域两边，他价差终究是要回归中间区间。


比如大盘弱的时候，可能在负50到0之间波动。行情好的时候在250-200区间波动
'''

LogDebug = functools.partial(print)

class okex_future(ccxt.okex):
    async def get_ticker(self, symbol, contract_type):
        '''
        contract_type: this_week, next_week, quarter
        '''
        params = {
            'symbol': symbol.replace('/', '_').lower(),
            'contract_type': contract_type,
        }
        try:
            response = await self.request('future_ticker', params=params)
        except:
            return None

        return response

async def save_tikcer(fp, obj, *args):
    ret = await obj.get_ticker(*args)
    if ret is None:
        return
    #pjson(ret)
    fp.write(str(time.time()) + '\t' + json.dumps(ret) + '\n')

g_running = True
def signal_handler(signum, frame):
    global g_running
    LogDebug('Signal handler called with signal', signum)
    g_running = False

class Runner():
    def __init__(self):
        pass

    def poll(self):
        pass

def pjson(j):
    print(json.dumps(j, indent=4))

def sleep(ms):
    time.sleep(ms/1000.0)

def mstime():
    return int(time.time() * 1000)

def main(argv=None):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    okf = okex_future()
    #rsp = okf.get_ticker('btc_usd', 'this_week')
    #pjson(rsp)
    #rsp = okf.get_ticker('btc_usd', 'quarter')
    #pjson(rsp)

    fname = get_strtime().replace(' ', '_').replace('/', '-').replace(':', '-')

    fp_list = []
    for k in ('this_week', 'next_week', 'quarter'):
        fp = open('{}_{}.txt'.format(fname, k), 'w')
        fp_list.append(fp)

    loop_interval = 1000

    runner = Runner()
    prev_loop_time = 0.0
    loop_count = -1
    while g_running:
        loop_count += 1
        curr_loop_time = mstime()
        loop_time_diff = curr_loop_time - prev_loop_time
        if loop_time_diff < loop_interval:
            sleep(loop_interval - loop_time_diff)
        prev_loop_time = mstime()

        li = []
        for i, k in enumerate(('this_week', 'next_week', 'quarter')):
            #li.append(okf.get_ticker('btc_usd', k))
            li.append(save_tikcer(fp_list[i], okf, 'btc_usd', k))

        asyncio.get_event_loop().run_until_complete(asyncio.gather(*li))
        #runner.poll()

    for fp in fp_list:
        fp.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
