#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import time

g_use_python3 = (sys.version_info[0] == 3)

exchanges = []

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1

ORDER_STATE_PENDING = 0
ORDER_STATE_CLOSED = 1
ORDER_STATE_CANCELED = 2

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
    print(*alt_args)

def LogStatus(*args):
    Log(*args)
def Sleep(ms):
    time.sleep(ms/1000.0)

class Exchange(object):
    def __init__(self, name):
        self.name = name
    def GetName(self):
        return self.name
    def GetCurrency(self):
        return 'QTUM_BTC'
    def GetAccount(self):
        return {'Balance': 100.0, 'FrozenBalance': 0.0,
                'Stocks': 101.0, 'FrozenStocks': 0.0}
    def GetTicker(self):
        if self.name == 'Binance':
            return {'High': 109.0, 'Low': 99.0, 'Buy': 98.0, 'Sell': 102,
                    'Last': 101.1, 'Volume': 1000.0}
        elif self.name == 'Huobi':
            return {'High': 109.0, 'Low': 99.0, 'Buy': 98.0, 'Sell': 102,
                    'Last': 102.1, 'Volume': 1000.0}
        else:
            return {'High': 109.0, 'Low': 99.0, 'Buy': 98.0, 'Sell': 102,
                    'Last': 103.1, 'Volume': 1000.0}
    def GetDepth(self):
        return {'Asks': [{'Price': 98.0, 'Amount': 10.0}],
                'Bids': [{'Price': 102.0, 'Amount': 8.0}]}
    def GetOrders(self):
        return [{'Id': 123, 'Price': 100.0, 'Amount': 9.0, 'DealAmount': 0.0,
                 'AvgPrice': 0.0, 'Status': ORDER_STATE_PENDING, 'Type': ORDER_TYPE_BUY}]
    def CancelOrder(self, order_id):
        return True
    def IO(self, *args):
        pass

exchanges.append(Exchange('Binance'))
exchanges.append(Exchange('Huobi'))
exchanges.append(Exchange('OKEX'))

def __main(argv=None):
    pass

if __name__ == '__main__':
    import sys
    sys.exit(__main(sys.argv))
