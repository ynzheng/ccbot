#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import ccxt
import json
import os
import os.path
import datetime
import time
import traceback
import getopt

g_use_python3 = (sys.version_info[0] == 3)
g_running = True

g_test_mode = False

class InfoSaver():
    def __init__(self, folder):
        self._folder = folder
        self._fobj = None

    def get_fname(self):
        now = get_strtime().replace('/', '-').replace(':', '-')
        date, time = now.split()
        h, m, s = time.split('-')
        #fname = os.path.join(self._folder, date, '%s-00-00.txt' % h)
        m = int(int(int(m) / 10) * 10)
        fname = os.path.join(self._folder, date, '%s-%02d-%s.txt' % (h, m, '00'))

        return fname

    def save(self, info):
        fname = self.get_fname()
        if self._fobj and self._fobj.name != fname:
            self._fobj.close()
            self._fobj = None

        if not self._fobj:
            dname = os.path.dirname(fname)
            if not os.path.isdir(dname):
                os.makedirs(dname)
            self._fobj = open(fname, 'w')

        print(info, file=self._fobj)

    def flush(self):
        if self._fobj:
            self._fobj.flush()

    def __del__(self):
        if self._fobj:
            self._fobj.close()

def get_strtime():
    global g_use_python3
    timefmt = '%Y/%m/%d %H:%M:%S'

    if g_use_python3:
        return  datetime.datetime.now(
                    datetime.timezone(              # pylint: disable=E1101
                        datetime.timedelta(hours=8)
                    )
                ).strftime(timefmt)
    else:
        import pytz
        tz = pytz.timezone('Asia/Shanghai')
        loc_dt = datetime.datetime.now(tz)
        return loc_dt.strftime(timefmt)

def _to_float_str(x, width, prec):
    # 0.00000001，总计占用 10 个字符
    # 
    if x is None:
        return '%*s' % (width, 'n/a')
    return '%*.*f' % (width, prec, x)

def ticker_to_info(ex, symbol, ticker, now,
                   price_width, price_prec,
                   amount_width, amount_prec):
    '''
    exchanges = [
        'okex',
        'huobipro',
        'binance',
        'zb',
        'quoinex',
        'poloniex',     # 有些网络访问会出问题
        'hitbtc',       # -> hitbtc2, 有些网络访问会出问题
    ]

    quoinex     btc/usd
    zb          btc/usdt
    binance     btc/usdt
    huobipro    btc/usdt
    okex        btc/usdt

    binance     qtum/btc
    huobipro    qtum/btc
    okex        qtum/btc
    '''
    global g_test_mode

    name = ex.id
    bid = ticker['bid']
    ask = ticker['ask']
    # NOTE: bidVolume 和 askVolume 存在歧义，因为为bidQty和askQty
    #       即 amount of bid 和 amount of ask
    bidVolume = None
    askVolume = None
    last = ticker['last']

    fob_params = {}
    need_fetch_order_book = False

    if name == 'binance':
        try:
            bidVolume = ticker['bidVolume']
            askVolume = ticker['askVolume']
        except:
            print(traceback.format_exc())
    elif name == 'huobipro':
        # 防止各种意外
        try:
            last = ticker['close']
        except:
            print(traceback.format_exc())
        try:
            bid = ticker['info']['bid'][0]
            bidVolume = ticker['info']['bid'][1]
        except:
            print(traceback.format_exc())
        try:
            ask = ticker['info']['ask'][0]
            askVolume = ticker['info']['ask'][1]
        except:
            print(traceback.format_exc())
    elif name == 'okex' or name == 'zb':
        need_fetch_order_book = True
        fob_params = {'size': 1}
    elif name == 'poloniex':
        need_fetch_order_book = True
        fob_params = {'depth': 1}
    elif name == 'hitbtc2':
        need_fetch_order_book = True
        fob_params = {'limit': 1}
    elif name == 'quoinex':
        need_fetch_order_book = True

    else:
        need_fetch_order_book = True

    if need_fetch_order_book:
        try:
            ob = ex.fetchOrderBook(symbol, params=fob_params)
            if g_test_mode:
                print(json.dumps(ob, indent=4))
        except ccxt.RequestTimeout:
            return None
        except:
            print(traceback.format_exc())
            return None
        # 以 order book 的信息为准，ticker的买1卖1信息可能不是最新
        try:
            if ob['bids']:
                bid = ob['bids'][0][0]
                bidVolume = ob['bids'][0][1]
        except:
            print(traceback.format_exc())
        try:
            if ob['asks']:
                ask = ob['asks'][0][0]
                askVolume = ob['asks'][0][1]
        except:
            print(traceback.format_exc())

    lst = [
        '%.6f' % now,
        ticker['timestamp'],
        ticker['datetime'],
        _to_float_str(bid, price_width, price_prec),
        _to_float_str(bidVolume, amount_width, amount_prec),
        _to_float_str(ask, price_width, price_prec),
        _to_float_str(askVolume, amount_width, amount_prec),
        # 成交量加权平均价格
        _to_float_str(ticker['vwap'], price_width, price_prec),
        # 现价
        _to_float_str(last, price_width, price_prec),
    ]

    return lst

def usage(cmd):
    msg = '''\
USAGE
    %s [OPTIONS] {exchange} {symbol}

OPTIONS
    --loop_interval_ms  ms          default 1000
    --print_interval    count       default 60
    --price_width       width       default 12
    --price_prec        prec        default 8
    --amount_width      width       default 12
    --amount_prec       prec        default 8

    --test              test mode
    ''' % cmd
    print(msg)

def parse_optitons(argv):
    cmd = argv[0]
    ret_opts = {}
    ret_args = []

    ret_opts['loop_interval_ms'] = 1000
    ret_opts['print_interval'] = 60
    ret_opts['price_width'] = 8 + 4
    ret_opts['price_prec'] = 8
    ret_opts['amount_width'] = 8 + 4
    ret_opts['amount_prec'] = 8
    ret_opts['test'] = False

    try:
        opts, ret_args = getopt.gnu_getopt(argv[1:], 'p:i:',
                                   ['help', 'test',
                                    'loop_interval_ms=',
                                    'print_interval=',
                                    'price_width=',
                                    'price_prec=',
                                    'amount_width=',
                                    'amount_prec='])
    except getopt.GetoptError as err:
        print(err)
        usage(cmd)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            usage(cmd)
            sys.exit(0)
        elif opt in ('-p', '--print_interval'):
            ret_opts['print_interval'] = int(arg)
        elif opt == '--test':
            ret_opts['test'] = True
        elif opt in ('-i', '--loop_interval_ms'):
            ret_opts['loop_interval_ms'] = int(arg)
        elif opt == '--price_width':
            ret_opts['price_width'] = int(arg)
        elif opt == '--price_prec':
            ret_opts['price_prec'] = int(arg)
        elif opt == '--amount_width':
            ret_opts['amount_width'] = int(arg)
        elif opt == '--amount_prec':
            ret_opts['amount_prec'] = int(arg)
        else:
            print('unhandled option:', opt, arg)
            usage(cmd)
            sys.exit(2)

    return ret_opts, ret_args

def main(argv):
    global g_running
    global g_test_mode

    opts, args = parse_optitons(argv)

    if len(args) < 2:
        usage(argv[0])
        return 2
    exchange = args[0]
    symbol = args[1].upper()

    price_prec = opts['price_prec']
    amount_prec = opts['amount_prec']
    price_width = opts['price_width']
    amount_width = opts['amount_width']

    loop_interval_ms = opts['loop_interval_ms']
    print_interval = opts['print_interval']

    g_test_mode = opts['test']

    curdir = os.path.abspath(os.curdir)
    folder = os.path.join(curdir, exchange, symbol.replace('/', '_'))

    saver = InfoSaver(folder)

    ex = eval('ccxt.%s()' % exchange)

    loop_count = 0
    prev_loop_time = 0.0
    stats_delay = 0.0 # second
    while g_running:
        if g_test_mode and loop_count >= 2:
            break

        loop_count += 1
        curr_loop_time = time.time()
        loop_time_diff_ms = (curr_loop_time - prev_loop_time) * 1000.0
        if loop_time_diff_ms < loop_interval_ms:
            time.sleep((loop_interval_ms - loop_time_diff_ms) / 1000.0)
        prev_loop_time = time.time()

        # 起始时间戳应该在这里
        now = time.time()
        try:
            ticker = ex.fetch_ticker(symbol)
        except ccxt.RequestTimeout:
            stats_delay += time.time() - prev_loop_time
            continue
        except:
            print(traceback.format_exc())
            stats_delay += time.time() - prev_loop_time
            continue

        if g_test_mode:
            print(json.dumps(ticker, indent=4))

        lst = ticker_to_info(ex, symbol, ticker, now,
                             price_width, price_prec,
                             amount_width, amount_prec)
        stats_delay += time.time() - prev_loop_time

        if not lst:
            continue
        lst = map(lambda x: str(x) if x else 'n/a', lst)
        info = '\t'.join(lst)
        if g_test_mode:
            print(info)
            break
        saver.save(info)

        if loop_count % print_interval == 0:
            #print(u'[%s][%s] 已记录%d条数据，平均网络延时为：%f秒'
            print('[%s][%s] saved %d records, average network delay is %f seconds'
                  % (exchange, symbol,
                     loop_count, stats_delay / float(print_interval)))
            stats_delay = 0.0
            saver.flush()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
