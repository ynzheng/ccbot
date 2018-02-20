#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ccxt
import texttable
import json
import time
import copy

"""
##############################
### tiker dict (from cryptopia)
{
    "info": {
        "SellVolume": 23.11321501,
        "Volume": 53.04537226,
        "LastPrice": 98556.2250002,
        "TradePairId": 5205,
        "SellBaseVolume": 14202973.45829993,
        "Label": "ETH/DOGE",
        "High": 105194.7092312,
        "BidPrice": 98556.2250002,
        "Low": 91297.0,
        "BuyBaseVolume": 9869539.43379357,
        "Close": 98556.2250002,
        "BaseVolume": 5130358.74236646,
        "Open": 103060.20080054,
        "AskPrice": 100822.99999999,
        "Change": -4.37,
        "BuyVolume": 13389125481.801765
    },
    "last": 98556.2250002,
    "timestamp": 1514112920560,
    "symbol": "ETH/DOGE",
    "vwap": null,
    "datetime": "2017-12-24T10:55:20.560Z",
    "high": 105194.7092312,
    "average": null,
    "low": 91297.0,
    "quoteVolume": 5130358.74236646,
    "ask": 100822.99999999,
    "close": 98556.2250002,
    "percentage": null,
    "baseVolume": 53.04537226,
    "open": 103060.20080054,
    "bid": 98556.2250002,
    "change": -4.37,
    "first": null
}

##############################
### markets dict (from okcoinusd)
{
    "ETC/USD": {
        "info": {
            "quoteCurrency": 3,
            "sort": 3,
            "maxPriceDigit": 3,
            "symbol": "etc_usd",
            "minTradeSize": 0.1,
            "marketFrom": 39,
            "maxSizeDigit": 4,
            "online": 1,
            "baseCurrency": 4,
            "productId": 1
        },
        "limits": {
            "amount": {
                "max": null,
                "min": 0.1
            },
            "cost": {
                "max": null,
                "min": null
            },
            "price": {
                "max": null,
                "min": null
            }
        },
        "quote": "USD",
        "symbol": "ETC/USD",
        "spot": true,
        "precision": {
            "amount": 4,
            "price": 3
        },
        "base": "ETC",
        "lot": 0.0001,
        "active": true,
        "future": false,
        "type": "spot",
        "id": "etc_usd"
    }
    ...
}

### order book
{
    "timestamp": 1514117969323,
    "bids": [
        [
            100003.0,
            0.0099108
        ],
        [
            100002.99999999,
            0.30692613
        ],
        [
            98469.39,
            0.03008525
        ],
        [
            98445.55555555,
            0.00813908
        ],
        [
            98444.44444444,
            0.00101377
        ]
    ],
    "asks": [
        [
            100826.99999999,
            0.03067318
        ],
        [
            100827.0,
            0.12
        ],
        [
            100828.99999979,
            0.1026231
        ],
        [
            100829.0,
            1.0
        ],
        [
            100829.82955932,
            1.90581538
        ]
    ],
    "datetime": "2017-12-24T12:19:29.323Z"
}
"""

g_a = \
{
    "timestamp": 1514125834600,
    "bids": [
        [
            96000.00000001,
            0.03789316
        ],
        [
            96000.0,
            0.07644389
        ],
        [
            95347.70783066,
            1.28665848
        ],
        [
            95347.70783061,
            0.0001054
        ],
        [
            95283.40499999,
            0.21743029
        ]
    ],
    "asks": [
        [
            96000.00000002,
            0.04960162
        ],
        [
            98748.5,
            0.02292241
        ],
        [
            98748.55555555,
            0.0020294
        ],
        [
            98748.67999995,
            0.00497
        ],
        [
            98748.71096168,
            0.00010177
        ]
    ],
    "datetime": "2017-12-24T14:30:34.600Z"
}

g_b = \
{
    "timestamp": 1514125840349,
    "bids": [
        [
            96005.0,
            0.02954094
        ],
        [
            96004.0,
            0.17714933
        ],
        [
            96000.0,
            0.00656879
        ],
        [
            95424.2135367,
            0.00213666
        ],
        [
            95000.0,
            0.00526
        ]
    ],
    "asks": [
        [
            97000.0,
            0.07186156
        ],
        [
            98330.05893908,
            0.00174793
        ],
        [
            98990.0,
            0.00204
        ],
        [
            98990.68965518,
            0.00112995
        ],
        [
            101000.0,
            0.01044
        ]
    ],
    "datetime": "2017-12-24T14:30:40.349Z"
}

def pp(dic):
    print(json.dumps(dic, indent=4))

def mainloop(argv):
    pass

def float_isclose(f1, f2, i):
    if abs(f1 - f2) < i:
        return True
    else:
        return False

def gen_order_book_row(exchg_name, order_book):
    tlst = []
    ulst = []
    for j in order_book.get('bids', []):
        tlst.append("%.8f" % j[0])
        ulst.append("%.8f" % j[1])
    buy_price = '\n'.join(tlst)
    buy_amount = '\n'.join(ulst)

    tlst = []
    ulst = []
    for j in order_book.get('asks', []):
        tlst.append("%.8f" % j[0])
        ulst.append("%.8f" % j[1])
    sell_price = '\n'.join(tlst)
    sell_amount = '\n'.join(ulst)

    return [exchg_name, buy_price, buy_amount, sell_price, sell_amount]

# TODO:
#   1. 添加考虑提现手续费
#   2. 添加考虑余额限制
# NOTE: 
#   - 暂时只支持按比率的交易手续费
#   - 暂时只支持固定值的提现手续费
def arbitrage_trade(bids, asks, bid_feerate=0, ask_feerate=0,
                    base_wdfee=0, quote_wdfee=0):
    '''根据参数进行套利交易，就是模拟股市的凑单交易，
    但是会计算套利和进行的交易单操作

    关于提现手续费：
    定价币（quote）的提现手续费直接在总体的盈利减掉就好了
    商品币（base）的提现手续费:
        x 在卖单那边少卖（具体看挂单的数量） - 理论上不选这种，因为套利靠卖不是靠买
        - 在买单那边多买（具体看挂单的数量）
    
    bid_feerate: 买方手续费，只支持固定费率的形式，如 0.2%
    ask_feerate: 卖方手续费，同上
    '''
    if not bids or not asks:
        return None
    if not bids[0][0] > asks[0][0]:
        return None

    # 通过先购买提现手续费来简易处理
    remain_fee = base_wdfee
    new_asks = []
    pre_order = []
    pre_cost = []
    # 遍历 asks 列表，知道把base的提现手续费买齐为止
    for iask in asks:
        if not remain_fee > 0:
            new_asks.append(iask)
            continue

        if remain_fee > iask[1] or float_isclose(remain_fee, iask[1],
                                                 0.0000000001):
            li = [iask[0], iask[1]]
            pre_order.append(li)
            pre_cost.append(iask[0] * iask[1])
            if float_isclose(remain_fee, iask[1], 0.0000000001):
                remain_fee = 0
            else:
                remain_fee -= iask[1]
        else:
            li = [iask[0], remain_fee]
            pre_order.append(li)
            pre_cost.append(iask[0] * remain_fee)
            new_asks.append([iask[0], iask[1] - remain_fee])
            remain_fee = 0

    biter = iter(bids)
    siter = iter(new_asks)
    buy = biter.next()
    sell = siter.next()

    pay_lst = []
    income_lst = []
    buy_order = []
    sell_order = []
    while buy[0] > sell[0] and not remain_fee > 0:
        try:
            if float_isclose(buy[1], sell[1], 0.0000000001):
                # 刚好买尽卖尽
                pay_lst.append((sell[0] * sell[1]) * (1 + bid_feerate))
                buy_order.append([sell[0], sell[1]])
                income_lst.append((buy[0] * buy[1]) * (1 - ask_feerate))
                sell_order.append([buy[0], buy[1]])
                buy = biter.next()
                sell = siter.next()
            elif buy[1] > sell[1]:
                # 能把对方卖的买完
                pay_lst.append((sell[0] * sell[1]) * (1 + bid_feerate))
                buy_order.append([sell[0], sell[1]])
                income_lst.append((buy[0] * sell[1]) * (1 - ask_feerate))
                sell_order.append([buy[0], sell[1]])
                buy = [buy[0], buy[1] - sell[1]]
                sell = siter.next()
            else:
                # 卖不完
                income_lst.append((buy[0] * buy[1]) * (1 - ask_feerate))
                sell_order.append([buy[0], buy[1]])
                pay_lst.append((sell[0] * buy[1]) * (1 + bid_feerate))
                buy_order.append([sell[0], buy[1]])
                sell = [sell[0], sell[1] - buy[1]]
                buy = biter.next()
        except StopIteration:
            break

    return {
        "cost": pay_lst,
        "bids": buy_order,
        "earn": income_lst,
        "asks": sell_order,
        "preOrder": pre_order,
        "preCost": pre_cost,
    }

def calculate_arbitrage(order_book_a, order_book_b, base_balance, quote_balance):
    '''
    假定两个交易所的仓位是一摸一样的，即base币都是一样的，quote币充足
    假设quote币不足，则会通过削减操作的仓位来实现套现（即即使可以卖光base币，
    也不能卖光，只卖quote能买到的base的量，最终保证base仓位一致）

    并且假定这个出价表在我们操作前不变，即100%成交

    费率暂不考虑，后期可以把费率直接算进收益削减里面
    C站的手续费全部算进quote的开销里面，可以确保买到base数值是对的
    '''
    a_buy1 = order_book_a['bids'][0] if order_book_a.get('bids', []) else 0
    a_sell1 = order_book_a['asks'][0] if order_book_a.get('asks', []) else -1
    b_buy1 = order_book_b['bids'][0] if order_book_b.get('bids', []) else 0
    b_sell1 = order_book_b['asks'][0] if order_book_b.get('asks', []) else -1

    # 最终要操作的买卖单
    tsell = None
    tbuy = None
    # 表示在哪家交易所交易，使用索引标识，0 为第一加，1为第二家，类推
    bidid = None
    askid = None
    bid_feerate = 0
    ask_feerate = 0

    a_feerate = 0.02 / 100
    b_feerate = 0.2  / 100

    base_wdfee_a = 0.005
    quote_wdfee_a = 3
    base_wdfee_b = 0.005
    quote_wdfee_b = 2

    base_wdfee = 0
    quote_wdfee = 0

    if a_buy1 > b_sell1 and b_sell1 > 0.0:
        # 可以套利，a卖，b买
        #print u"可以套利，a卖，b买"
        tbuy = order_book_a['bids']
        tsell = order_book_b['asks']
        bidid = 1
        askid = 0
        bid_feerate = b_feerate
        ask_feerate = a_feerate
        base_wdfee = base_wdfee_b
        quote_wdfee = quote_wdfee_a
    elif b_buy1 > a_sell1 and a_sell1 > 0.0:
        # 可以套利，b卖，a买
        #print u"可以套利，b卖，a买"
        tbuy = order_book_b['bids']
        tsell = order_book_a['asks']
        bidid = 0
        askid = 1
        bid_feerate = a_feerate
        ask_feerate = b_feerate
        base_wdfee = base_wdfee_a
        quote_wdfee = quote_wdfee_b
    else:
        # 不能套利
        return None

    result = arbitrage_trade(tbuy, tsell, bid_feerate, ask_feerate,
                             base_wdfee, quote_wdfee)
    result['bidid'] = bidid
    result['askid'] = askid
    return result

def draw_order_book(symbol, name_a, order_book_a, name_b, order_book_b):
    '''简单地打印两个交易所当前的挂单情况'''
    txttlb = texttable.Texttable()
    txttlb.set_cols_align(['l', 'r', 'r', 'r', 'r'])
    txttlb.header(["Exchange\n(%s)" % symbol,
                   'Buy Price',
                   'Buy Amount',
                   'Sell Price',
                   'Sell Amount'])
    txttlb.add_row(gen_order_book_row(name_a, order_book_a))
    txttlb.add_row(gen_order_book_row(name_b, order_book_b))

    print(txttlb.draw())

def draw_arbitrage_order(symbol, name_a, name_b, arbitrage_result):
    '''打印可以套利的情况下，在两个交易所所下的买卖挂单'''
    result = arbitrage_result
    result_table = texttable.Texttable()
    result_table.set_cols_align(['l', 'r', 'r', 'r', 'r'])
    result_table.header(["Exchange\n(%s)" % symbol,
                         'Buy Price',
                         'Buy Amount',
                         'Sell Price',
                         'Sell Amount'])

    ob_a = {}
    ob_b = {}
    if result.get('bidid') == 0:
        ob_a['bids'] = result['bids']
    elif result.get('bidid') == 1:
        ob_b['bids'] = result['bids']

    if result.get('askid') == 0:
        ob_a['asks'] = result['asks']
    elif result.get('askid') == 1:
        ob_b['asks'] = result['asks']
    result_table.add_row(gen_order_book_row(name_a, ob_a))
    result_table.add_row(gen_order_book_row(name_b, ob_b))
    print(result_table.draw())

def draw_arbitrage_summary(arbitrage_result):
    precision = 8
    result = arbitrage_result
    sum_tbl = texttable.Texttable()
    sum_tbl.set_precision(precision)
    sum_tbl.header(['Order', 'Cost', 'Earn', 'Profit', "Profit Rate (%)"])
    sum_tbl.set_cols_align(['c', 'c', 'c', 'c', 'c'])
    cost = 0.0
    earn = 0.0
    for i, j in enumerate(result['cost']): # cost 和 earn 数量肯定是相同的
        cost += result['cost'][i]
        earn += result['earn'][i]
        profit = earn - cost
        profit_percent = (profit / cost) * 100
        sum_tbl.add_row([i + 1,
                         cost,
                         earn,
                         profit,
                         profit_percent])

    print(sum_tbl.draw())

def print_exchange_info(symbol, name_a, order_book_a, name_b, order_book_b):
    timefmt = '%Y/%m/%d %H:%m:%S %z'
    timefmt2 = '%Y/%m/%d %H:%m:%S'
    print('========== %s ==========' % time.strftime(timefmt))
    ta = time.strftime(timefmt2, time.localtime(order_book_a['timestamp']/1000))
    tb = time.strftime(timefmt2, time.localtime(order_book_b['timestamp']/1000))
    nta = name_a + '\n\n' + '\n'.join(ta.split())
    ntb = name_b + '\n\n' + '\n'.join(tb.split())
    draw_order_book(symbol, nta, order_book_a, ntb, order_book_b)

    result = calculate_arbitrage(order_book_a, order_book_b, 0, 0)

    if result is None:
        print(u'XXXXX 无法套利 XXXXX')
        return
    else:
        print(u"########## 可以套利: ##########")

    draw_arbitrage_order(symbol, name_a, name_b, result)
    draw_arbitrage_summary(result)
    print(result['preOrder'])
    print(result['preCost'])

def main(argv):
    delay = 1

    all_dict = {
        'ETH/DOGE': [
            'cryptopia',
            'yobit',
        ],
        #'ETH/USDT': [
            #'cryptopia',
            #'yobit',
        #],
    }

    #tikers = cpia.fetch_ticker('ETH/DOGE')
    #pp(tikers)
    local_data = True
    if not local_data:
        cryptopia = ccxt.cryptopia()
        yobit = ccxt.yobit()
        oba = cryptopia.fetch_order_book('ETH/DOGE', {'orderCount': 5})
        obb = yobit.fetch_order_book('ETH/DOGE', {'limit': 5})
        name_a = cryptopia.name
        name_b = yobit.name
        pp(oba)
        pp(obb)
    else:
        name_a = "Cryptopia"
        name_b = "YoBit"
        oba = g_a
        obb = g_b
    print_exchange_info('ETH/DOGE', name_a, oba, name_b, obb)

    if local_data:
        return

    for symbol, v in all_dict.iteritems():
        exlst = []
        for idx, ex in enumerate(v):
            exlst.append(eval('ccxt.%s()' % ex))
            #print(exlst[idx].name)

        if not exlst:
            print('%s can not be exchange in any exchang' % symbol)
            continue
        if len(exlst) == 1:
            print("%s can only be exchange in %s\n" % (symbol, exlst[0].name))
            continue

        # TODO: 需要两两组合来测试
        # 暂时只处理首两个交易所的测试
        oblst = []
        for ex in exlst:
            if ex.name == 'Cryptopia':
                oblst.append(ex.fetch_order_book(symbol, {'orderCount': 5}))
            elif ex.name == 'YoBit':
                oblst.append(ex.fetch_order_book(symbol, {'limit': 5}))
            else:
                oblst.append(ex.fetch_order_book(symbol))

        print_exchange_info(symbol,
                            exlst[0].name, oblst[0],
                            exlst[1].name, oblst[1])


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
