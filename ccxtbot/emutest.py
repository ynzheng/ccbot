#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import time
import copy
import decimal
from ccorder_chart import ExchangeRecords

g_use_python3 = (sys.version_info[0] == 3)

_exchange_names = (
    'binance',
    'huobipro',
    #'okex',
    #'zb',
)
_st = '2018/01/21 00:00:00'
_et = '2018/01/21 23:59:59'
_symbol = 'QTUM_BTC'
_folder = 'data'

exchanges = []

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1

ORDER_STATE_PENDING = 0
ORDER_STATE_CLOSED = 1
ORDER_STATE_CANCELED = 2

# 获取滴答的函数, 用来调试
_get_tick = None
# 支持单元测试
g_unittest = False

def Log(*args):
    if g_use_python3:
        alt_args = args
    else:
        alt_args = []
        for arg in args:
            if isinstance(arg, unicode):
                alt_args.append(arg)
            else:
                alt_args.append(str(arg).decode('utf-8'))
    if type(_get_tick) == type(Log):
        print('[%08d]' % _get_tick(), *alt_args) # pylint: disable=E1102
    else:
        print(*alt_args)

def LogDebug(*args):
    return Log(*args)
def LogError(*args):
    return Log(*args)
def LogTrade(*args):
    return Log(*args)
def LogStatus(*args):
    return Log(*args)
def LogProfit(*args):
    Log('Profit:', *args)
def LogProfitReset(*args):
    pass
def Sleep(ms):
    time.sleep(ms/1000.0)

def _CDelay(*args):
    pass
def GetCommand():
    return None
def _N(f, prec):
    prec = int(prec)
    assert prec > 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_DOWN))

def draw_table(*tables):
    if not tables:
        return

    ts = []
    for table in tables:
        if isinstance(table, list):
            for t in table:
                ts.append(t)
        else:
            ts.append(table)

    import texttable
    prec = 8
    for table in ts:
        tab = texttable.Texttable(0)
        tab.set_precision(prec)

        header = []
        for i in table['cols']:
            if g_use_python3:
                header.append(i)
            else:
                header.append(i.decode('utf-8'))

        tab.header(header)
        align = ['c'] * len(table['cols'])
        tab.set_cols_align(align)
        tab.set_cols_dtype(['t'] * len(table['cols']))
        tab.add_rows(table['rows'], header=False)
        Log(tab.draw())
    #Log('@' * 80)

class Exchange(object):
    _oid = 0
    FEES_MODE_FORWARD = 0
    FEES_MODE_BALANCE = 1

    def __init__(self, name):
        self.name = name
        self.currency = 'QTUM_BTC'
        self.buy_fee = 0.0
        self.sell_fee = 0.0

        self._prev_record = None
        self._curr_record = None
        self._pend_record = None
        self._records = []
        self._index = 0

        self.fees_mode = self.FEES_MODE_FORWARD
        #self.fees_mode = self.FEES_MODE_BALANCE

        self.account = {
            'Balance': 0.0,
            'FrozenBalance': 0.0,
            'Stocks': 0.0,
            'FrozenStocks': 0.0,
        }

        # *** 以下供单元测试的时候定制用 ***
        self.ticker = {
            'High'  : 0.0,
            'Low'   : 0.0,
            'Sell'  : 0.0,
            'Buy'   : 0.0,
            'Last'  : 0.0,
            'Volume': 0.0,
        }
        self.depth = {
            'Asks': [
                {
                    'Price' : 0.0,
                    'Amount': 0.0,
                }
            ],
            'Bids': [
                {
                    'Price' : 0.0,
                    'Amount': 0.0,
                }
            ]
        }
        self.GetOrders_return = []
        #self.GetOrders_return = [
        #    {
        #        'Id': 2,
        #        'Price': 1.0,
        #        'Amount': 3.0,
        #        'DealAmount': 2.0,
        #        'AvgPrice': 1.5,
        #        'Status': ORDER_STATE_PENDING,
        #        'Type': ORDER_TYPE_BUY,
        #    },
        #]
        self.buy_fail = False
        self.sell_fail = False
        self.cancel_fail = False

    def _init_ExchangeRecords(self):
        global _symbol, _st, _et, _folder
        self._exr = ExchangeRecords(self.name, _symbol,
                                       _st, _et, _folder)

    def _get_new_record(self):
        if self._index < len(self._records):
            self._curr_record = self._records[self._index]
            self._index += 1
            return self._curr_record

        records = self._exr.get_one_file_raw_records()
        if not records:
            return None
        assert len(records) <= 600

        # 修剪这 600 个 record
        new_records = []
        stime = int(float(records[0][0]))
        for idx in range(600):
            if len(new_records) >= 600:
                break

            if idx == 0:
                record = records[0]
                record[0] = int(float(record[0]))
                new_records.append(record)
                continue
            if idx >= len(records):
                record = records[-1]
                record[0] = stime + idx
                new_records.append(record)
                continue

            prev_record = new_records[-1]
            curr_record = records[idx]
            curr_record[0] = int(float(curr_record[0]))

            diff = int(float(curr_record[0])) - int(float(prev_record[0]))

            if diff == 1:
                new_records.append(curr_record)

            # 处理跳秒的情况 78 -> 81
            elif diff > 1:
                for i in range(diff - 1):
                    if len(new_records) >= 600:
                        break
                    # 0 1 -> 79 80
                    record = copy.deepcopy(prev_record)
                    record[0] += (1 + i)
                    new_records.append(record)
                if len(new_records) >= 600:
                    break
                new_records.append(curr_record)

            # 1516464080.081566
            # 1516464080.646304
            elif diff == 0:
                # 同秒的情况，用最新的吧，舍弃旧的
                new_records[-1] = curr_record

        try:
            assert len(new_records) == 600
        except:
            print(len(new_records), '!=', 600)
            print(self._exr._fp.name, len(records))
            raise
        self._records = new_records
        self._index = 1
        self._curr_record = self._records[0]
        return self._curr_record

    def _set_account(self, Balance=0.0, Stocks=0.0, FrozenBalance=None, FrozenStocks=None):
        self.account['Balance'] = Balance
        self.account['Stocks'] = Stocks
        if not FrozenBalance is None:
            self.account['FrozenBalance'] = FrozenBalance
        if not FrozenStocks is None:
            self.account['FrozenStocks'] = FrozenStocks

    def _set_currency(self, currency):
        self.currency = currency

    def _set_trade_fee(self, buy_fee, sell_fee):
        self.buy_fee = buy_fee
        self.sell_fee = sell_fee

    def GetName(self):
        return self.name
    def GetCurrency(self):
        return self.currency
    def GetAccount(self):
        return copy.deepcopy(self.account)
    def GetTicker(self):
        if g_unittest:
            return copy.deepcopy(self.ticker)
        record = self._curr_record
        result = {
            #'High': 0.0,
            #'Low': 0.0,
            #'Volume': 0.0,
            'Buy': float(record[3]),
            'Sell': float(record[5]),
            'Last': float(record[8]),
        }
        return result
    def GetDepth(self):
        if g_unittest:
            return copy.deepcopy(self.depth)
        record = self._curr_record
        return {'Asks': [{'Price': float(record[5]), 'Amount': float(record[6])}],
                'Bids': [{'Price': float(record[3]), 'Amount': float(record[4])}]}
    def GetOrders(self):
        return copy.deepcopy(self.GetOrders_return)
    def CancelOrder(self, order_id):
        if self.cancel_fail:
            return False
        return True
    def IO(self, *args):
        pass
    def Buy(self, price, amount):
        if self.buy_fail:
            return None
        prec = 8
        buy_fee_ratio = self.buy_fee / 100.0
        if self.fees_mode == self.FEES_MODE_FORWARD:
            cost = price * amount
            earn_stocks = amount * (1.0 - buy_fee_ratio)
        else:
            cost = price * amount * (1.0 + buy_fee_ratio)
            earn_stocks = amount
        if self.account['Balance'] < cost:
            LogError('[%s] 买入失败：余额 %.*f < %.*f'
                     % (self.name, prec, self.account['Balance'], prec, cost))
            return None
        self.account['Balance'] -= cost
        self.account['Stocks'] += earn_stocks

        type(self)._oid += 1
        LogDebug('[%s] Buy(%.8f, %.8f) = %d, cost Balance %.8f, earn Stocks %.8f'
                 % (self.name, price, amount, type(self)._oid, cost, earn_stocks))
        return type(self)._oid

    def Sell(self, price, amount):
        if self.sell_fail:
            return None
        prec = 8
        if self.account['Stocks'] < amount:
            LogError('[%s] 卖出失败：余币 %.*f < %.*f'
                     % (self.name, prec, self.account['Stocks'], prec, amount))
            return None
        sell_fee_ratio = self.sell_fee / 100.0
        earn = price * amount * (1.0 - sell_fee_ratio)
        self.account['Balance'] += earn
        self.account['Stocks'] -= amount

        type(self)._oid += 1
        LogDebug('[%s] Sell(%.8f, %.8f) = %d, earn Balance %.8f, cost Stocks %.8f'
                 % (self.name, price, amount, type(self)._oid, earn, amount))
        return type(self)._oid

for i in _exchange_names:
    exchanges.append(Exchange(i))
del i
exchange = exchanges[0]

def __main(argv=None):
    import base64
    import rsa
    from rsa import PublicKey, PrivateKey
    b64pubk = b'UHVibGljS2V5KDk5MzQzMTY5NDM4MzgzOTEwOTY2NjYwNTU3MDEzNzIzMzIwNTQ1MjI1MzI4MDc3MzQ5MTA3MzgzNDIyOTE3MjE0OTQ0NTM5MDY3ODA5MTkyMjE3MzcyMjU0NTUzMDgzNTA4MzI3MjI5NDgwMzI3NTY5NDkzMDMzMTk2ODA3MTMwNTQwMTg1MjQ5NDc2MTg3MzEyMjc2MDEzMzEsIDY1NTM3KQ=='
    pubk = eval(base64.b64decode(b64pubk))
    msg = str(int(time.time())).encode()
    enmsg = rsa.encrypt(msg, pubk)
    import strategy2 as m
    return m.run(enmsg, globals())

    for e in exchanges:
        e._init_ExchangeRecords()
    e = exchanges[0]
    for i in range(10):
        for e in exchanges:
            #e._get_new_record()
            print(i+1, e._get_new_record())
            print(e.GetTicker())
            print(e.GetDepth())

if __name__ == '__main__':
    import sys
    sys.exit(__main(sys.argv))
