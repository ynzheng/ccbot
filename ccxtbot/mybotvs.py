#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import time
import traceback
import copy
import json
import ccxt

__all__ = [
    'exchanges',
    'exchange',
    'ORDER_TYPE_BUY',
    'ORDER_TYPE_SELL',
    'ORDER_STATE_PENDING',
    'ORDER_STATE_CLOSED',
    'ORDER_STATE_CANCELED',
    'Exchange',
    'Log',
    'LogDebug',
    'LogError',
    'LogProfit',
    'LogProfitReset',
    'LogStatus',
    'Sleep',
]

_g_use_python3 = (sys.version_info[0] == 3)

exchanges = []
exchange = None

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1

ORDER_STATE_PENDING = 0
ORDER_STATE_CLOSED = 1
ORDER_STATE_CANCELED = 2

_get_tick = None
def Log(*args):
    if _g_use_python3:
        alt_args = args
    else:
        alt_args = []
        for arg in args:
            if isinstance(arg, unicode):
                alt_args.append(arg)
            else:
                alt_args.append(str(arg).decode('utf-8'))
    if type(_get_tick) == type(Log):
        print('[%08d]' % _get_tick(), *alt_args)
    else:
        print(*alt_args)

def LogDebug(*args):
    return Log(*args)
def LogError(*args):
    return Log(*args)
def LogStatus(*args):
    return Log(*args)
def LogProfit(*args):
    Log('Profit:', *args)
def LogProfitReset(*args):
    pass
def Sleep(ms):
    time.sleep(ms/1000.0)

def pjson(j):
    print(json.dumps(j, indent=4, sort_keys=True))

_g_name_dict = {
    'hitbtc': 'hitbtc2',
    'huobi': 'huobipro',
}

def conv_ticker(ticker, name=''):
    result = {}
    result['High'] = ticker['high']
    result['Low'] = ticker['low']
    result['Last'] = ticker['last']
    # FIXME
    result['Volume'] = ticker['baseVolume']

    if name == 'binance':
        result['Buy'] = ticker['bid']
        result['Sell'] = ticker['ask']
    elif name == 'huobipro':
        try:
            result['Last'] = ticker['close']
            bid = ticker['info']['bid'][0]
            ask = ticker['info']['ask'][0]
            result['Buy'] = bid
            result['Sell'] = ask
        except:
            LogDebug(traceback.format_exc())

    return result

def conv_depth(depth):
    # {'Price': 0, 'Amount': 0}
    result = {
        'Bids': [],
        'Asks': [],
    }

    d = {}
    for i in depth.get('bids', []):
        d['Price'] = i[0]
        d['Amount'] = i[1]
    if d:
        result['Bids'].append(d)

    d = {}
    for i in depth.get('asks', []):
        d['Price'] = i[0]
        d['Amount'] = i[1]
    if d:
        result['Asks'].append(d)
    return result

def conv_orders(orders):
    '''
    {
        Id          :交易单唯一标识
        Price       :下单价格
        Amount      :下单数量
        DealAmount  :成交数量
        AvgPrice    :成交均价，                     # 注意 ，有些交易所不提供该数据，不提供的设置为 0 。 
        Status      :订单状态, 参考常量里的订单状态
        Type        :订单类型, 参考常量里的订单类型
    }
    '''
    result = []
    for order in orders:
        o = {}
        o['Id'] = order.get('id')
        o['Price'] = order.get('price')
        o['Amount'] = order.get('amount')
        o['DealAmount'] = order.get('filled')
        o['AvgPrice'] = None    # 这个一般没有，我们不管
        o['Status'] = ORDER_STATE_PENDING
        if order.get('side') == 'buy':
            o['Type'] = ORDER_TYPE_BUY
        else:
            o['Type'] = ORDER_TYPE_SELL
        result.append(o)

    return result

def get_depth_limit_param(name, limit=1):
    param = {}
    if name in {'okex', 'zb'}:
        param['size'] = limit
    elif name == 'poloniex':
        param['depth'] = limit
    elif name == 'hitbtc2':
        param['limit'] = limit

    return param

class Exchange(object):
    _oid = 0

    def __init__(self, name, symbol, apiKey='', secret=''):
        self.name = name
        self.currency = symbol.replace('/', '_').upper()
        self.account = {
            'Balance': 0.0,
            'FrozenBalance': 0.0,
            'Stocks': 0.0,
            'FrozenStocks': 0.0,
        }
        self.base, self.quote = self.currency.split('_')

        self._symbol = self.currency.replace('_', '/')
        self._name = _g_name_dict.get(name.lower(), name.lower())
        self.ccxtobj = eval('ccxt.%s()' % self._name)
        self.ccxtobj.apiKey = apiKey
        self.ccxtobj.secret = secret

        self.depth = None
        self.depth_timestamp = 0.0

    def GetName(self):
        return self.name
    def GetCurrency(self):
        return self.currency

    def _create_order(self, side, price, amount):
        '''
        return = {
            // order id
            'id': 'string',
            // decoded original JSON response from the exchange as is
            'info': { ... },
        }
        '''
        return self.ccxtobj.create_order(self._symbol, 'limit', side, amount, price)

    def Buy(self, price, amount):
        # NOTE: 即使发送失败，也可能下单成功了，要以最新的结果(GetOrders)为准
        try:
            ret = self._create_order('buy', price, amount)
        except:
            LogDebug(traceback.format_exc())
            return None
        LogDebug(ret)
        return ret['id']

    def Sell(self, price, amount):
        # NOTE: 即使发送失败，也可能下单成功了，要以最新的结果(GetOrders)为准
        try:
            ret = self._create_order('sell', price, amount)
        except:
            LogDebug(traceback.format_exc())
            return None
        LogDebug(ret)
        return ret['id']

    def GetAccount(self):
        ret = self.ccxtobj.fetchBalance()
        base = self.base
        quote = self.quote
        self.account['Balance'] = ret[quote]['free']
        self.account['FrozenBalance'] = ret[quote]['used']
        self.account['Stocks'] = ret[base]['free']
        self.account['FrozenStocks'] = ret[base]['used']
        return copy.deepcopy(self.account)

    def GetTicker(self):
        '''
        {
            High    :最高价
            Low     :最低价
            Sell    :卖一价
            Buy     :买一价
            Last    :最后成交价
            Volume  :最近成交量
        }
        '''
        try:
            raw_ticker = self.ccxtobj.fetchTicker(self._symbol)
        except:
            LogDebug(traceback.format_exc())
            return None
        ticker = conv_ticker(raw_ticker, self._name)
        if 'Buy' in ticker and 'Sell' in ticker:
            return ticker

        try:
            depth = self.ccxtobj.fetchOrderBook(
                self._symbol, params=get_depth_limit_param(self._name))
        except:
            LogDebug(traceback.format_exc())
            return None
        self.depth = depth
        self.depth_timestamp = time.time()

        if depth['bids']:
            ticker['Buy'] = depth['bids'][0][0]
        else:
            # FIXME
            ticker['Buy'] = 0.0
        if depth['asks']:
            ticker['Sell'] = depth['asks'][0][0]
        else:
            # FIXME
            ticker['Sell'] = 0.0

        return ticker

    def GetDepth(self, limit=1):
        # 一定时间内重新获取的话，直接返回
        if time.time() - self.depth_timestamp <= 0.01:
            return conv_depth(self.depth)

        try:
            depth = self.ccxtobj.fetchOrderBook(self._symbol,
                                                get_depth_limit_param(self._name,
                                                                      limit))
            return conv_depth(depth)
        except:
            LogDebug(traceback.format_exc())
            return None

    def GetOrders(self):
        try:
            orders = self.ccxtobj.fetchOpenOrders(self._symbol)
        except:
            LogDebug(traceback.format_exc())
            return None
        return conv_orders(orders)

    def CancelOrder(self, oid):
        try:
            # Cryptopia:
            #   ret = {
            #       "Data": [
            #           266376624
            #       ],
            #       "Error": null,
            #       "Success": true
            #   }
            ret = self.ccxtobj.cancel_order(oid, self._symbol)
            return ret
        except:
            LogDebug(traceback.format_exc())
            return False

    def IO(self, *args):
        pass

def _init(exlist, symbol=''):
    '''
    _init([{'name': 'huobi', 'symbol': 'qtum/btc'}])
    _init([['huobi', 'qtum/btc'], ['okex', 'qtum/btc']])
    _init(['huobi', 'okex'], 'qtum/btc')
    '''
    global exchanges
    global exchange
    del exchanges[:]
    exchange = None
    for item in exlist:
        if isinstance(item, dict):
            inst = Exchange(item['name'], item['symbol'],
                            item.get('apiKey', ''), item.get('secret', ''))
        elif isinstance(item, list):
            inst = Exchange(item[0], item[1])
        else:
            inst = Exchange(item, symbol)
        exchanges.append(inst)
    exchange = exchanges[0]

#__symbol = 'eth/btc'
#exchanges.append(Exchange('OKEX', __symbol))
#exchanges.append(Exchange('Binance', __symbol))
#exchanges.append(Exchange('Huobi', __symbol))
#exchange = exchanges[0]
#del __symbol

def __main(argv=None):
    with open('exchanges.json') as fp:
        _init(json.load(fp))
    for e in exchanges:
        pjson(e.GetTicker())
    #pjson(exchange.GetAccount())
    #if exchange._symbol == 'DOGE/USDT':
        #pjson(exchange.Sell(10000000.0, 0.1))
    orders = exchange.GetOrders()
    pjson(orders)
    #for o in orders:
        #pjson(exchange.CancelOrder(o['Id']))
    #print(exchange.GetDepth())

if __name__ == '__main__':
    import sys
    sys.exit(__main(sys.argv))
