#!/usr/bin/env python3
#cython: language_level=3, boundscheck=False
# -*- coding: utf-8 -*-

import time
import json
import asyncio
from aiohttp import web
import ccxt.async as ccxt
import traceback
import sys

__all__ = []

g_version_info = (1, 0, 2)
g_version = '.'.join(map(str, g_version_info))

g_debug = True

def logdbg(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    file = kwargs.get('file', sys.stdout)
    flush = kwargs.get('flush', False)
    print(*args, sep=sep, end=end, file=file, flush=flush)

# {
#   'binance': {'BTC/USDT': exchange}
#   ...
# }
g_ccxt_exchanges = {}

g_exchange_name_dict = {
    'huobi': 'huobipro',
    'hitbtc': 'hitbtc2',
}

def norm_name(name):
    global g_exchange_name_dict
    n = name.lower()
    return g_exchange_name_dict.get(n, n)

def norm_symbol(symbol):
    s = symbol.replace('_', '/').upper()
    return s

def split_symbol(symbol):
    s = norm_symbol(symbol)
    li = s.split('/')
    if len(li) < 2:
        return [li[0], li[0]]
    else:
        return li

def mstime():
    return int(time.time() * 1000)

def get_ccxt_exchange(name, symbol, apiKey, secret):
    global g_ccxt_exchanges
    name = norm_name(name)
    symbol = norm_symbol(symbol)
    d0 = g_ccxt_exchanges.setdefault(name, {})
    try:
        if symbol in d0:
            exchange = d0[symbol]
        else:
            exchange = eval('ccxt.%s()' % name)
            d0[symbol] = exchange
        exchange.apiKey = apiKey
        exchange.secret = secret
    except:
        raise
    return exchange

async def get_handler(request):
    name = request.match_info.get('name', 'Anonymouse')
    text = repr(request)
    return web.Response(text=text)

def conv_account(account, base, quote):
    '''
    {
        'data': [
            {'currency': 'btc', 'free': 1.2, 'frozen': 0.1},
            ...
        ]
    }
    '''
    result = {'data': []}

    # 没有符号参数的话，就返回全部余额信息
    if not base and not quote:
        for currency in account:
            #if currency in {'info', 'free', 'used', 'total'}:
                #continue
            if not currency.isupper():
                continue
            result['data'].append({
                'currency': currency.lower(),
                'free':     account[currency]['free'],
                'frozen':   account[currency]['used'],
            })
        return result

    for currency in (base, quote):
        if not currency:
            continue
        result['data'].append({
            'currency': currency.lower(),   # 这里好像要求小写
            'free':     account[currency]['free'],
            'frozen':   account[currency]['used']
        })

    return result

def conv_ticker(ticker, name=''):
    '''
    {
        'data': {
            'time': int(time.time() * 1000),
            'buy': 0,
            'sell': 0,
            'last': 0,
            'high': 0,
            'low': 0,
            'vol': 0,
        }
    }
    '''
    result = {}
    data = {'time': mstime()}

    for k in ('high', 'low', 'last'):
        data[k] = ticker[k]

    data['vol'] = ticker['baseVolume']

    if name in {'binance', 'yobit'}:
        data['buy'] = ticker['bid']
        data['sell'] = ticker['ask']
    elif name == 'huobipro':
        try:
            data['last'] = ticker['close']
            bid = ticker['info']['bid'][0]
            ask = ticker['info']['ask'][0]
            data['buy'] = bid
            data['sell'] = ask
        except:
            raise
    else:
        if not ticker['bid'] is None:
            data['buy'] = ticker['bid']
        if not ticker['ask'] is None:
            data['sell'] = ticker['ask']

    result['data'] = data
    return result

def conv_depth(depth):
    '''
        {
            'data': {
                'time': x,
                'asks': [[], []],
                'bids': [[], []],
            }
        }
    '''
    result = {'data': {'time': mstime(), 'asks': [], 'bids': []}}
    result['data'].update(depth)
    return result

def conv_trade_ret(ret):
    '''
    NOTE: cryptopia (id = None，即下单即完全成交，为下单成功)
    {
        "cost": 0.0019219199999999997,
        "id": null,
        "side": "buy",
        "datetime": "2018-02-14T06:34:27.436Z",
        "symbol": "ETC/BTC",
        "status": "open",
        "timestamp": 1518590067436,
        "fee": null,
        "price": 0.004004,
        "filled": null,
        "type": "limit",
        "remaining": 0.48,
        "info": {
            "Data": {
                "FilledOrders": [
                    48724654
                ],
                "OrderId": null
            },
            "Success": true,
            "Error": null
        },
        "amount": 0.48
    }
    '''
    id = ret['id']
    if id is None:  # 下单成功，但是没有返回有效的订单号，Cryptopia 会这样
        # NOTE: 我们认为，返回的订单号为 0 的话，即表示已经完全成交
        id = '0'    # FIXME: 需要确认没有交易所以 0 作为订单号
    return {'data': {'id': id}}

def conv_orders(orders):
    '''
    {
        'data': [{
            'id': 1,
            'amount': 0,
            'price': 0,
            'deal_amount': 0,
            'type': 'buy'/'sell',
            'status': 'open',
        }, {
            ...
        }]
    }
    '''
    result = {}
    data = []
    for order in orders:
        o = {}
        for k in ('id', 'amount', 'price'):
            o[k] = order[k]
        o['type'] = order['side']
        o['deal_amount'] = order['filled']
        o['status'] = 'open',
        data.append(o)

    result['data'] = data
    return result

def conv_cancel_ret(ret):
    '''
    {
        'data': true/false,
    }
    '''
    # TODO
    return {'data': bool(ret)}

async def post_handler(request):
    '''
    {
        'access_key': '',
        'secret_key': '',
        'nonce': '',
        'method': '',
        'params': {'symbol': 'ETH_BTC'},
    }
    '''
    #logdbg(request)
    result = None

    name = norm_name(request.match_info.get('name', ''))
    reqd = await request.json()
    method = reqd.get('method')
    # NOTE: GetAccount 没有传入 symbol 参数！
    symbol = norm_symbol(reqd.get('params', {}).get('symbol', ''))
    base, quote = split_symbol(symbol)
    apiKey = reqd.get('access_key', '')
    secret = reqd.get('secret_key', '')
    try:
        ex = get_ccxt_exchange(name, symbol, apiKey, secret)
        if method == 'accounts':
            account = await ex.fetch_balance()
            result =  conv_account(account, base, quote)
        elif method == 'ticker':
            ticker = await ex.fetch_ticker(symbol)
            result = conv_ticker(ticker, name)
            if not 'buy' in result['data'] or not 'sell' in result['data']:
                depth = await ex.fetch_order_book(symbol)
                if depth['bids']:
                    result['data']['buy'] = depth['bids'][0][0]
                else:
                    result['data']['buy'] = 0.0
                if depth['asks']:
                    result['data']['sell'] = depth['asks'][0][0]
                else:
                    result['data']['sell'] = 0.0
        elif method == 'depth':
            depth = await ex.fetch_order_book(symbol)
            result = conv_depth(depth)
        elif method == 'trade':
            side = reqd['params']['type']
            price = float(reqd['params']['price'])
            amount = float(reqd['params']['amount'])
            ret = await ex.create_order(symbol, 'limit', side, amount, price)
            result = conv_trade_ret(ret)
        elif method == 'orders':
            orders = await ex.fetch_open_orders(symbol)
            result = conv_orders(orders)
        elif method == 'cancel':
            oid = reqd['params']['id']
            try:
                ret = await ex.cancel_order(oid, symbol)
            except:
                ret = False
            result = conv_cancel_ret(ret)
        elif method == 'trades':
            result = {'error': 'Not Implemented'}
        elif method == 'records':
            result = {'error': 'Not Implemented'}
        elif method == 'order':
            result = {'error': 'Not Implemented'}
        else:
            result = {'error': 'Not Implemented'}
    except:
        logdbg(time.asctime())
        logdbg(traceback.format_exc())
        errmsg = str(sys.exc_info()[1])
        result = {
            'error': errmsg,
        }

    if not result:
        result = {'error': 'timeout'}
    return web.Response(text=json.dumps(result))

def main(argv):
    host = '127.0.0.1'
    port = 12345
    try:
        host = argv[1]
        port = int(argv[2])
    except IndexError:
        pass
    logdbg('version', g_version)
    app = web.Application()
    app.router.add_get('/', get_handler)
    app.router.add_get('/{name}', get_handler)
    app.router.add_post('/{name}', post_handler)
    web.run_app(app, host=host, port=port)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
