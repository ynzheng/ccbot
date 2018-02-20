'''backtest
start: 2018-01-30 00:00:00
end: 2018-01-31 00:00:00
period: 15m
exchanges: [{"eid":"OKEX","currency":"LTC_BTC","balance":3,"stocks":185},{"eid":"Huobi","currency":"LTC_BTC","balance":3,"stocks":185}]
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import sys
import random
import traceback
import copy
import decimal
import platform
import json
import random
import datetime

g_use_python3 = (sys.version_info[0] == 3)

g_startup_time = ''
g_run_on_botvs = True

# 这个可以作为时间戳，策略的时间戳精度即为轮询间隔
g_loop_count = 0
# 此次套利的所有的交易所
g_myex_list = []
g_all_init_fund = {}

# 最后一次下单的时间戳，无论什么方式的下单都更新，如 套利，平仓
g_last_order_timestamp = 0
# 最后一次取消订单的时间戳
g_last_cancel_order_timestamp = 0
# 最后一次进行套利交易的时间戳
g_last_arbitrage_timestamp = 0

g_stats = {
    # FIXME 处理取消了订单的情况
    # 套利收益，这是成功套利后的收益，也就是买和卖都成交后计算的差价收益
    # 如果在一次买卖套利当中，买卖成交量不相等，只能计算买/卖最小成交量为套利收益
    # 未能成交部分，额，暂时不知道算到哪里，只能算是一次套利失败后的常规成交单
    # 这部分成交量统计到交易所的总共成交量里面
    'STATS_ARBITRAGE_PROFIT': 0.0,
}

# 全部的脚本参数的默认值
ALL_PARAMETERS = {
    # 调试模式会打印更多信息
    'G_PARAM_DEBUG_MODE': True,

    # 模拟测试模式，即用历史数据测试，无需实时获取信息来测试
    # 在botvs平台无法使用此模式
    'G_PARAM_EMUTEST_MODE': True,

    # 最大的统一精度，一般取为所有交易所中精度最大的值
    # 现在所知为 8，因为 BTC 的最小单位“聪”即为 8 位小数精度
    'G_PARAM_MAX_UNIFY_PREC': 8,

    # 计算套利时，是否忽略交易手续费？
    # 计算套利时，一般可以认为差价必须大于 (买手续费 + 卖手续费 + 套利差) 才可以套利
    # 如果忽略手续费的话，直接使用套利差来计算，这时候套利差的设置必须考虑手续费率
    # 这个选项一般不需要导出，使用默认值即可
    'G_PARAM_IGNORE_TRADE_FEE': False,

    # 这个数字越大，每单成交数量越大，越小成交单拆分越多。
    # 假如差价区间为 5%，则套利交易数量会扩大为 5 * 此参数
    'G_PARAM_TRADE_AMOUNT_MAGIC': 7,

    # ==================== 以上参数不导出，仅内部使用 ====================

    # 轮询间隔，毫秒
    'G_PARAM_LOOP_INTERVAL': 1000,

    # 是否优先使用 websocket 模式
    # 一般 websocket 提供更低的延时，但不是每个交易所都支持
    'G_PARAM_USE_WEBSOCKET': True,

    # botvs 平台上的测试模式，仅在 botvs 平台上运行时才有效
    # 即所有交易都是模拟的，不是实际连接到交易所交易
    'G_PARAM_BOTVS_TEST_MODE': False,
    # 模拟模式的账号余额，实盘模式会忽略此参数
    'G_PARAM_EMU_BALANCE': 0.075,
    # 模拟模式的账号余币，实盘模式会忽略此参数
    'G_PARAM_EMU_STOCKS': 20.0,
    # 模拟模式进行套利交易后，暂停检测套利的轮询次数
    # 因为模拟模式的交易不影响市场，所以如果套利后不暂停，
    # 可能会马上再进行同样的套利，虽然会受余额限制。
    # 不暂停就设置为 0
    'G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE': 10,

    # 订单冻结超过此轮询次数后才会取消
    'G_PARAM_WAIT_FOR_ORDER': 10,

    # 套利差，百分率
    # 使用场景：
    #   - 计算套利交易时，和交易费率一起算作基本交易成本
    'G_PARAM_ARBITRAGE_DIFFERENCE': 0.25,

    # 一般设置为每次套利的基本成交数量
    # 这个参数作为以下的调整依据：
    #   - 套利时，以此为基础乘以一个策略系数得出策略目标交易数量
    'G_PARAM_BASE_TRADE_AMOUNT': 5,

    # 每单的最少交易数量
    # 这个一般根据交易所的限制设置，如有些交易所对某些币有最小交易量限制的话
    # 如果交易所没有最小交易数量限制的话，一般设置为交易数量精度的最小单位
    # 如交易数量精度为 4，则最小交易量可设置为 0.0001
    'G_PARAM_MIN_TRADE_AMOUNT': 0.01,

    # 为了套利交易的快速成交，买卖时需要额外付出的价格，最小可设置为 0.0
    # 套利差会在滑点造成的更小差价(-滑点*2)的基础上计算
    # 所以可能由于滑点的原因导致套利差变化
    'G_PARAM_SLIP_POINT': 0.0,

    # 最大差价
    # 这个对差价过大的交易所作调整用的，设置为你看到过的交易所间的最大差价。
    'G_PARAM_MAX_DIFF': 0.00005,

    # NOTE: 这是自定义的精度
    #   - 只在最后执行买/卖时才会按照这个精度截断价格/交易数量
    #   - 只在记录买/卖价格/交易数量时，才截断数值
    # 其他时候直接使用python的float数据结构（总计17位的精度）
    # 价格精度，小数点后位数
    'G_PARAM_PRICE_PREC': 6,

    # NOTE: 同上
    # 交易数量精度，小数点后位数
    'G_PARAM_AMOUNT_PREC': 2,

    # 交易费率(%), 按买卖顺序添加
    # 如你的交易所顺序为 okex, zb, 交易费率为 0.1, 0.1, 0.2, 0.2
    # 则表示 okex 的买手续费为 0.1%, 卖手续费为 0.1%, zb 的分别为 0.2% 和 0.2%
    'G_PARAM_TRADE_FEE': ' , , , , , , 0.1, 0.1',
}

def get_param(name, default=None):
    '''获取策略参数'''
    global ALL_PARAMETERS
    try:
        exec('global %s' % name)
        return eval(name)
    except NameError:
        return ALL_PARAMETERS.get(name, default)

def get_loop_count():
    global g_loop_count
    return g_loop_count

try:
    exchanges
    def LogDebug(*args):
        if get_param('G_PARAM_DEBUG_MODE'):
            return Log(*args)
    def LogError(*args):
        return Log(*args)
except NameError:
    g_run_on_botvs = False
    if get_param('G_PARAM_EMUTEST_MODE'):
        from emutest import *
        if get_param('G_PARAM_DEBUG_MODE'):
            import emutest
            emutest._get_tick = get_loop_count
    else:
        from botvs import *

g_real_arbit_diff = get_param('G_PARAM_ARBITRAGE_DIFFERENCE')

DEFAULT_TRDFEE = {'Buy': 0.25, 'Sell': 0.25 }

TRDFEE_DICT = {
    "binance": {
        "Buy": 0.1, 
        "Sell": 0.1
    }, 
    "bitflyer": {
        "Buy": 0.01, 
        "Sell": 0.01
    }, 
    "bitfinex": {
        "Buy": 0.2, 
        "Sell": 0.2
    }, 
    "coincheck": {
        "Buy": 0, 
        "Sell": 0
    }, 
    "hitbtc": {
        "Buy": 0.1, 
        "Sell": 0.1
    }, 
    "huobi": {
        "Buy": 0.2, 
        "Sell": 0.2
    }, 
    "huobipro": {
        "Buy": 0.2, 
        "Sell": 0.2
    }, 
    "kraken": {
        "Buy": 0.26, 
        "Sell": 0.26
    }, 
    "okcoin_en": {
        "Buy": 0.2, 
        "Sell": 0.2
    }, 
    "okex": {
        "Buy": 0.1, 
        "Sell": 0.1
    }, 
    "quoine": {
        "Buy": 0, 
        "Sell": 0
    }, 
    "quoinex": {
        "Buy": 0, 
        "Sell": 0
    }, 
    "zb": {
        "Buy": 0, 
        "Sell": 0
    }, 
    "zaif": {
        "Buy": -0.01, 
        "Sell": -0.01
    }
}

def add_stats(key, val):
    global g_stats
    g_stats[key] += val

def get_stats(key):
    global g_stats
    return g_stats.get(key)

def is_bottest_mode():
    '''
    botvs 平台上的测试模式
    - 返回的 account 为固定值
    - 买卖一定成功
    - 每次买卖后，下次更新account，直接从上次的买卖数据计算
    - 其他和 viewer 一样
    '''
    return g_run_on_botvs and get_param('G_PARAM_BOTVS_TEST_MODE')

def is_emutest_mode():
    '''
    用数据库的历史记录模拟测试
    '''
    if g_run_on_botvs:
        return False
    return get_param('G_PARAM_EMUTEST_MODE', True)

def is_debug_mode():
    return get_param('G_PARAM_DEBUG_MODE', False)

def touch_last_order_timestamp():
    global g_last_order_timestamp
    g_last_order_timestamp = get_loop_count()

def touch_last_cancel_order_timestamp():
    global g_last_cancel_order_timestamp
    g_last_cancel_order_timestamp = get_loop_count()

def touch_last_arbitrage_timestamp():
    global g_last_arbitrage_timestamp
    g_last_arbitrage_timestamp = get_loop_count()

def get_last_order_timestamp():
    global g_last_order_timestamp
    return g_last_order_timestamp

def get_last_cancel_order_timestamp():
    global g_last_cancel_order_timestamp
    return g_last_cancel_order_timestamp

def get_last_arbitrage_timestamp():
    global g_last_arbitrage_timestamp
    return g_last_arbitrage_timestamp

def get_strtime():
    global g_use_python3
    #timefmt = '%Y/%m/%d %H:%M:%S %z'
    timefmt = '%Y/%m/%d %H:%M:%S'

    if g_use_python3:
        return  datetime.datetime.now(
                    datetime.timezone(              # pylint: disable=E1101
                        datetime.timedelta(hours=8)
                    )
                ).strftime(timefmt)
    else:
        import pytz # pylint: disable=F0401
        tz = pytz.timezone('Asia/Shanghai')
        loc_dt = datetime.datetime.now(tz)
        return loc_dt.strftime(timefmt)

def bytes2str(data):
    if not g_use_python3:            return data

    if isinstance(data, bytes):      return data.decode()
    #if isinstance(data, (str, int)): return str(data)
    if isinstance(data, dict):       return dict(map(bytes2str, data.items()))
    if isinstance(data, tuple):      return tuple(map(bytes2str, data))
    if isinstance(data, list):       return list(map(bytes2str, data))
    if isinstance(data, set):        return set(map(bytes2str, data))

    return data

def norm4json(data):
    '''把 dict, tuple, list, set 的 bytes, 实例, 转为字符串'''
    if isinstance(data, bytes):      return data.decode()
    if isinstance(data, dict):       return dict(map(norm4json, data.items()))
    if isinstance(data, tuple):      return tuple(map(norm4json, data))
    if isinstance(data, list):       return list(map(norm4json, data))
    if isinstance(data, set):        return set(map(norm4json, data))
    # complex 要转为字符串
    if isinstance(data, (int, float, bool)):    return data

    return str(data)

def pjson(j):
    Log(json.dumps(norm4json(j), indent=4, sort_keys=True))

class MyExchange(object):
    def __init__(self, botvs_exchange):
        global TRDFEE_DICT
        ### ========== 基础信息, 只读, 不变 ==========
        self.botvs_exchange = botvs_exchange
        self.born_time = time.time()

        self.currency = bytes2str(self.botvs_exchange.GetCurrency())
        self.base, self.quote = currency_to_base_quote(self.currency)

        # 这两个信息只要一次获取即可
        self.name = bytes2str(self.botvs_exchange.GetName())

        # 精度，一般交易所的精度都是小数点后 8 位
        self.price_prec = get_param('G_PARAM_PRICE_PREC')
        self.amount_prec = get_param('G_PARAM_AMOUNT_PREC')
        ### ----------------------------------------

        ### ========== account, ticker, depth ==========
        ### ticker 每 tick 必须刷新, account 和 depth 可按需刷新
        if is_bottest_mode():
            self.account = {
                'Balance': get_param('G_PARAM_EMU_BALANCE'),
                'Stocks': get_param('G_PARAM_EMU_STOCKS'),
                'FrozenBalance': 0.0,
                'FrozenStocks': 0.0,
            }
        else:
            self.account = bytes2str(self.botvs_exchange.GetAccount())
            if not self.account:
                # 初始化的时候，可以重试一次
                self.account = bytes2str(self.botvs_exchange.GetAccount())
        self.ticker = bytes2str(self.botvs_exchange.GetTicker())
        if not self.ticker:
            # 初始化的时候，可以重试一次
            self.ticker = bytes2str(self.botvs_exchange.GetTicker())
        self.depth = None
        ### ----------------------------------------
        try:
            assert not self.account is None
            assert not self.ticker is None
        except AssertionError:
            Log('[%s] 初始化时无法从网络获取必要的数据，请重试。' % self.name)
            raise

        # 标记以下 3 个信息的最后更新的时间(tick)
        self.account_tick = 0           # 表示轮询时处理过 account 信息了
        self.account_update_tick = 0    # 从网络上获取最新的信息时的 tick
        self.account_change_tick = 0    # 表示检测到 account 变化时的 tick
        self.ticker_tick = 0
        self.depth_tick = 0

        # 记录初始化的时候的基本信息
        self.init_account = copy.deepcopy(self.account)

        # 后续可重新设置手续费
        self.trdfee = TRDFEE_DICT.get(self.name.lower(), DEFAULT_TRDFEE)
        self.api_mode = 'REST' # 默认为 'REST', 有些交易所支持 'websocket'
        self.delay = 0.0

        # 'refresh_instant'     - 立即刷新
        # 'refresh_random'      - 随机刷新
        # 'refresh_complete'    - 刷新完成
        # 因为一般交易所的api实现用，获取account信息延时都比较大，
        # 并且，如果没有发生交易，account的状态理论上是不变的
        # 所以刷新account需要优化
        #   - 只有执行交易操作后，才需要刷新account
        #   - 观察的时候，轮询N次后才刷新一次
        self.account_refresh_state = 'refresh_complete'

        self.executed_orders = {}

        # for botvs test mode
        self.next_account = copy.deepcopy(self.account)
        self._oid = 0

    def __repr__(self):
        return 'MyExchange(%s)' % repr(self.name)

    def __str__(self):
        return self.__repr__()

    def is_latest(self):
        tick = get_loop_count()
        return self.account_tick == tick and self.ticker_tick == tick and self.depth_tick == tick

    def set_trade_fee(self, buy_fee=None, sell_fee=None):
        if not buy_fee is None:
            self.trdfee['Buy'] = float(buy_fee)
        if not sell_fee is None:
            self.trdfee['Sell'] = float(sell_fee)

    def get_buy1_price(self):
        '''如果 depth 和 ticker 都是最新, 以 depth 的为准, 否则以 ticker 为准'''
        if self.ticker_tick == self.depth_tick:
            if self.depth and self.depth['Bids']:
                return self.depth['Bids'][0]['Price']
            else:
                return self.ticker['Buy']
        else:
            return self.ticker['Buy']

    def get_sell1_price(self):
        '''如果 depth 和 ticker 都是最新, 以 depth 的为准, 否则以 ticker 为准'''
        if self.ticker_tick == self.depth_tick:
            if self.depth and self.depth['Asks']:
                return self.depth['Asks'][0]['Price']
            else:
                return self.ticker['Sell']
        else:
            return self.ticker['Sell']

    def get_last_price(self):
        return self.ticker['Last']

    def get_buy1_amount(self):
        if self.depth and self.depth['Bids']:
            return self.depth['Bids'][0]['Amount']
        return 0.0

    def get_sell1_amount(self):
        if self.depth and self.depth['Asks']:
            return self.depth['Asks'][0]['Amount']
        return 0.0

    def clean_data(self):
        '''仅清空延时和深度'''
        self.depth = None
        self.delay = 0.0

    def _emu_buy(self, price, amount):
        buy_fee_ratio = self.trdfee['Buy'] / 100.0
        cost = price * amount * (1.0 + buy_fee_ratio)
        if self.next_account['Balance'] < cost:
            LogError('买入失败：余额 %.8f < %.8f'
                     % (self.next_account['Balance'], cost))
            return None
        self.next_account['Balance'] -= cost
        self.next_account['Stocks'] += amount
        self._oid += 1
        return self._oid

    def buy(self, price, amount):
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        # NOTE: 这里不能 round，只在执行 buy 之前 round
        #real_price = round_buy_price(price)
        #real_amount = round_amount(amount)
        real_price = price
        real_amount = amount
        if is_bottest_mode():
            oid = self._emu_buy(price, amount)
        else:
            oid = self.botvs_exchange.Buy(real_price, real_amount)
        Log('[%s] buy(%.*f, %.*f) = %s' % (self.name,
                                           self.price_prec, real_price,
                                           self.amount_prec, real_amount,
                                           repr(oid)))
        return bytes2str(oid)

    def _emu_sell(self, price, amount):
        if self.next_account['Stocks'] < amount:
            LogError('卖出失败：余币 %.8f < %.8f'
                     % (self.next_account['Stocks'], amount))
            return None
        sell_fee_ratio = self.trdfee['Sell'] / 100.0
        earn = price * amount * (1.0 - sell_fee_ratio)
        self.next_account['Balance'] += earn
        self.next_account['Stocks'] -= amount
        self._oid += 1
        return self._oid

    def sell(self, price, amount):
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        # NOTE: 这里不能 round，只在执行 sell 之前 round
        #real_price = round_sell_price(price)
        #real_amount = round_amount(amount)
        real_price = price
        real_amount = amount
        if is_bottest_mode():
            oid = self._emu_sell(price, amount)
        else:
            oid = self.botvs_exchange.Sell(real_price, real_amount)
        Log('[%s] sell(%.*f, %.*f) = %s' % (self.name,
                                            self.price_prec, real_price,
                                            self.amount_prec, real_amount,
                                            repr(oid)))
        return bytes2str(oid)

    def get_account(self):
        if is_bottest_mode():
            self.account = copy.deepcopy(self.next_account)
            return self.account
        account = bytes2str(self.botvs_exchange.GetAccount())
        if account is None:
            LogError('[%s] 获取 Account 数据失败' % self.name)
            return None
        if self.account != account:
            self.account_change_tick = get_loop_count()
        self.account = account
        self.account_refresh_state = 'refresh_complete'
        return self.account

    def get_ticker(self):
        ticker = bytes2str(self.botvs_exchange.GetTicker())
        if ticker is None:
            LogError('[%s] 获取 Ticker 数据失败' % self.name)
            return None
        # High    :最高价
        # Low     :最低价
        # Sell    :卖一价
        # Buy     :买一价
        # Last    :最后成交价
        # Volume  :最近成交量
        #for k in ('High', 'Low', 'Sell', 'Buy', 'Last', 'Volume')
        for k in ('Sell', 'Buy', 'Last'): # 我们只用这 3 个值
            v = ticker.setdefault(k, 0.0)
            if not isinstance(v, (int, float)):
                ticker[k] = 0.0
        self.ticker = ticker
        return self.ticker

    def get_depth(self):
        depth = bytes2str(self.botvs_exchange.GetDepth())
        if depth is None:
            LogError('[%s] 获取 Depth 数据失败' % self.name)
            return None
        self.depth = depth
        return self.depth

    def get_orders(self):
        if is_bottest_mode():
            return []
        return bytes2str(self.botvs_exchange.GetOrders())

    def cancel_order(self, oid, buy_or_sell=None):
        if buy_or_sell:
            Log('[%s] cancel %s order: %s' % (self.name, buy_or_sell, str(oid)))
        else:
            Log('[%s] cancel order: %s' % (self.name, str(oid)))
        if is_bottest_mode():
            return True
        return self.botvs_exchange.CancelOrder(oid)

    def _make_arbit_trade(self, myex_b, slip_point=0.0):
        '''
        根据当前买1卖1的挂单计算套利交易
        '''
        a = self
        b = myex_b

        result = caculate_arbitrage(self, myex_b, slip_point=slip_point)
        if not result:
            return None

        # 订单薄可能为空，例如没有任何人挂单
        if not a.depth:
            abuy1_amount = 0.0
            asell1_amount = 0.0
        else:
            if a.depth.get('Asks', []):
                asell1_amount = a.depth['Asks'][0]['Amount']
            else:
                asell1_amount = 0.0
            if a.depth.get('Bids', []):
                abuy1_amount = a.depth['Bids'][0]['Amount']
            else:
                abuy1_amount = 0.0

        if not b.depth:
            bbuy1_amount = 0.0
            bsell1_amount = 0.0
        else:
            if b.depth.get('Asks', []):
                bsell1_amount = b.depth['Asks'][0]['Amount']
            else:
                bsell1_amount = 0.0
            if b.depth.get('Bids', []):
                bbuy1_amount = b.depth['Bids'][0]['Amount']
            else:
                bbuy1_amount = 0.0

        if result['direction'] == 'asbb':
            # a卖b买
            result['amount'] = min(abuy1_amount, bsell1_amount)
        elif result['direction'] == 'abbs':
            # a买b卖
            result['amount'] = min(asell1_amount, bbuy1_amount)
        else:
            result = None

        return result

    def make_arbit_trade(self, myex_b, slip_point=0.0):
        amount_prec = self.amount_prec
        trade = self._make_arbit_trade(myex_b, slip_point=slip_point)
        if not trade:
            return None

        buy_myex = trade['buy_myex']
        sell_myex = trade['sell_myex']

        min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
        if sell_myex.account['Stocks'] > (buy_myex.account['Stocks'] + min_trade_amount) * 8:
            # 卖单的交易所的商品币是买单的交易所的商品币的 8 倍还多
            # 此次套利的交易量可以扩大
            strategy_amount = (sell_myex.account['Stocks'] - buy_myex.account['Stocks']) * 0.6
        else:
            diff = trade['sell_price'] - trade['buy_price']
            try:
                trade_amount_magic = get_param('G_PARAM_TRADE_AMOUNT_MAGIC')
                param = diff / (trade['buy_price'] / (trade_amount_magic*100.0))
            except ZeroDivisionError:
                Log('ZeroDivisionError: %s' % json.dumps(norm4json(trade)))
                param = 1.0
            strategy_amount = get_param('G_PARAM_BASE_TRADE_AMOUNT') * param

        max_sell_amount = sell_myex.account['Stocks']
        try:
            max_buy_amount = float(buy_myex.account['Balance']) / trade['buy_price']
        except ZeroDivisionError:
            return None
        min_in_three = min(max_sell_amount, max_buy_amount, trade['amount'])
        if strategy_amount < min_trade_amount:
            strategy_amount = min_trade_amount
        if strategy_amount > min_in_three:
            strategy_amount = min_in_three

        if min_in_three < min_trade_amount:
            return None

        # 根据策略算出的交易量，这是在之前算得的交易量上微调得到的，更新的结果
        trade['strategy_amount'] = strategy_amount
        # 即为“最大可买量”，“最大可卖量”，“买1卖1撮合交易量”中最小值
        trade['min_in_three'] = min_in_three
        # 最大的可以买的量，最大的可以卖的量，根据买卖挂单算的可以买卖的最小量
        trade['max_buy_amount'] = max_buy_amount
        trade['max_sell_amount'] = max_sell_amount
        return trade

def caculate_price_diff(last_price_diff,
                        sell_price, sell_fee,
                        buy_price, buy_fee):
    '''
    比较两个交易所的差价
    last_price_diff 为 a 和 b 交易所最后成交价的差价
    sell_price 为卖单交易所的卖价格，一般为订单薄的买1价
    sell_fee 百分率
    buy_price 为买单交易所的买价格，一般为订单薄的卖1价
    buy_fee 百分率
    '''
    global g_real_arbit_diff
    max_diff = abs(get_param('G_PARAM_MAX_DIFF'))
    alt_arbit_diff_percent = g_real_arbit_diff

    # 如果当前最后成交差价达到了最大差价的 70% 以上，可以扩大套利差
    if abs(last_price_diff) > max_diff * 0.7:
        ratio = abs(last_price_diff) / max_diff
        alt_arbit_diff_percent += ratio * alt_arbit_diff_percent

    buy_fee_ratio = buy_fee / 100.0
    sell_fee_ratio = sell_fee / 100.0
    # NOTE: 把套利差算到费率那里，其实是指每次套利必须至少获取此比例的利润
    fee_ratio = alt_arbit_diff_percent / 100.0
    # 计算套利时，可以忽略交易的手续费，这只在有特殊需要的时候才使用
    if not get_param('G_PARAM_IGNORE_TRADE_FEE'):
        price_diff = sell_price - buy_price \
                   - sell_price * sell_fee_ratio \
                   - buy_price * buy_fee_ratio \
                   - buy_price * fee_ratio
    else:
        price_diff = sell_price - buy_price \
                   - buy_price * fee_ratio


    return price_diff

def caculate_arbitrage(myex_a, myex_b, slip_point=0.0):
    '''
    根据当前买1卖1的挂单计算套利交易
    把“滑点”也考虑了
    '''
    result = {}

    a = myex_a
    b = myex_b

    a_sell_price = a.get_buy1_price() - slip_point
    a_buy_price = a.get_sell1_price() + slip_point

    b_sell_price = b.get_buy1_price() - slip_point
    b_buy_price = b.get_sell1_price() + slip_point

    if a_sell_price <= 0.0 or a_buy_price <= 0.0 or \
       b_sell_price <= 0.0 or b_buy_price <= 0.0:
        return None

    last_price_diff = a.get_last_price() - b.get_last_price()

    # 为了确保执行设定的套利差起到了实际的作用，计算的时候需要按精度凑整
    a_diff = caculate_price_diff(last_price_diff,
                                 round_sell_price(a_sell_price), a.trdfee['Sell'],
                                 round_buy_price(b_buy_price), b.trdfee['Buy'])
    b_diff = caculate_price_diff(last_price_diff,
                                 round_sell_price(b_sell_price), b.trdfee['Sell'],
                                 round_buy_price(a_buy_price), a.trdfee['Buy'])

    if a_diff > 0:
        # a卖b买
        result['sell_myex'] = a
        result['sell_price'] = a_sell_price
        result['buy_myex'] = b
        result['buy_price'] = b_buy_price
        result['diff'] = a_diff
        result['direction'] = 'asbb'
    elif b_diff > 0:
        # a买b卖
        result['sell_myex'] = b
        result['sell_price'] = b_sell_price
        result['buy_myex'] = a
        result['buy_price'] = a_buy_price
        result['diff'] = b_diff
        result['direction'] = 'abbs'
    else:
        result = None

    return result

def clean_exchange_data(myex_list, loop_count):
    for myex in myex_list:
        myex.clean_data()

def fetch_exchange_data(myex_list, myex_comp_list, loop_count):
    # NOTE: 如果获取失败，保留上一次的数据，绝不会清空数据，这个原则很实用
    #       如果要标记数据是过时的，只需要一个变量即可达到
    for idx, myex in enumerate(myex_list): # Account
        if myex.account_refresh_state == 'refresh_instant' or \
           (myex.account_refresh_state == 'refresh_random' and \
            loop_count % 60 == (59 - idx)): # 让交易所在不同的循环更新
        # 状态为立即更新 或者 到了随机刷新的时候，才执行刷新
            t0 = time.time()
            ret = myex.get_account()
            myex.delay += (time.time() - t0) * 1000
            myex.account_refresh_state = 'refresh_complete'
            if ret is None:
                Log('%s: 获取 Account 数据失败（%s）'
                    % (myex.name,
                       '立即' if myex.account_refresh_state == 'refresh_instant' else '随机'))
            else:
                myex.account_update_tick = loop_count
                myex.account_tick = loop_count
        else:
            myex.account_tick = loop_count

    for myex in myex_list: # Ticker
        t0 = time.time()
        ret = myex.get_ticker()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.ticker_tick = loop_count

    for myex in myex_list: # Depth
        t0 = time.time()
        ret = myex.get_depth()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.depth_tick = loop_count

def generate_compare_list(myex_list):
    li = []
    ll = len(myex_list) - 1
    for i in range(ll):
        for j in range(ll - i):
            li.append((myex_list[i], myex_list[i+j+1]))
    return li

def float_round_up(f, prec):
    assert isinstance(prec, int)
    assert prec > 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_UP))

def float_round_down(f, prec):
    assert isinstance(prec, int)
    assert prec > 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_DOWN))

def round_buy_price(buy_price):
    return float_round_up(buy_price, get_param('G_PARAM_PRICE_PREC'))

def round_sell_price(sell_price):
    return float_round_down(sell_price, get_param('G_PARAM_PRICE_PREC'))

def round_amount(amount):
    return float_round_down(amount, get_param('G_PARAM_AMOUNT_PREC'))

def make_arbit_trades(myex_comp_list):
    '''
    计算应该执行的套利交易单子
    '''
    result = []
    slip_point = get_param('G_PARAM_SLIP_POINT')
    for (myex_a, myex_b) in myex_comp_list:
        if not myex_a.is_latest() or not myex_b.is_latest():
            continue
        if myex_a.delay >= 2000 or myex_b.delay >= 2000:
            continue
        try:
            trade = myex_a.make_arbit_trade(myex_b, slip_point=slip_point)
            if trade:
                result.append(trade)
        except AssertionError:
            raise
        except:
            Log('WTF on ARBITRAGE!')
            Log(traceback.format_exc())

    return result

def process_arbitrage_trade(trade, max_trade_amount):
    '''
    trade结构是一个套利交易对，如 a卖b买

    return 买单id，卖单id，交易数量
    '''
    sell_myex = trade['sell_myex']
    buy_myex = trade['buy_myex']
    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
    if max_trade_amount < min_trade_amount:
        Log('本轮套利中，前几次的套利交易已经用尽了资金，放弃此次套利。')
        LogDebug(json.dumps(norm4json(trade)))
        return None, None, 0.0

    target_amount = trade['strategy_amount']
    if target_amount > max_trade_amount:
        target_amount = max_trade_amount

    target_amount = round_amount(target_amount)
    if target_amount < min_trade_amount:
        # 最小交易量统一在制作订单的时候检查了，所以这里应该很少可能打印
        LogDebug('该次交易数量 %.*f 少于策略设置的最小交易量 %.*f，放弃执行交易。'
                 % (buy_myex.amount_prec, target_amount,
                    buy_myex.amount_prec, min_trade_amount))
        return None, None, 0.0

    target_buy_price = round_buy_price(trade['buy_price'])
    target_sell_price = round_sell_price(trade['sell_price'])

    # @ 买入
    buy_order_id = buy_myex.buy(target_buy_price, target_amount)
    if not buy_order_id:
        Log('下单失败：以 %.*f 价格买入 %.*f %s，取消此次套利交易'
            % (buy_myex.price_prec, target_buy_price,
               buy_myex.amount_prec, target_amount, buy_myex.base))
        return None, None, 0.0
    else:
        buy_myex.executed_orders[buy_order_id] = {
            'type': 'buy',
            'price': target_buy_price,
            'amount': target_amount,
            'tick': get_loop_count(),
            'pair_myex': sell_myex,     # 记录配对的信息
        }
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()

    # @ 卖出
    sell_order_id = sell_myex.sell(target_sell_price, target_amount)
    if not sell_order_id:
        Log('下单失败：以 %.*f 价格卖出 %.*f %s，但是套利买单已经下单成功...'
            % (sell_myex.price_prec, target_sell_price,
               sell_myex.amount_prec, target_amount, sell_myex.base))
        # 下单失败也要继续
        #return buy_order_id, None, target_amount
    else:
        sell_myex.executed_orders[sell_order_id] = {
            'type': 'sell',
            'price': target_sell_price,
            'amount': target_amount,
            'tick': get_loop_count(),
            'pair_myex': buy_myex,
        }
        buy_myex.executed_orders[buy_order_id]['pair'] = sell_order_id
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()

    if buy_order_id and sell_order_id:
        fee = (target_sell_price * sell_myex.trdfee['Sell'] + \
               target_buy_price * buy_myex.trdfee['Buy']) * target_amount / 100.0
        arbitrage_profit = (target_sell_price - target_buy_price) * target_amount
        arbitrage_profit -= fee
        add_stats('STATS_ARBITRAGE_PROFIT', arbitrage_profit)

    return buy_order_id, sell_order_id, target_amount

def process_arbitrage_trades(myex_list, all_trade_list):
    '''
    返回交易数量
    '''
    if not all_trade_list:
        return 0.0

    sorted_list = sorted(all_trade_list, key=lambda k: k['diff'], reverse=True)

    # NOTE: 如果 all_trade_list 的数量大于 1，则两个交易单可能会重叠
    #       如 a，b，c三个交易时，(a, b), (a, c) 都有可执行的交易，
    #       则第 2 个交易单的数据可能是不准确的，此时可能无法满足买卖单的情况
    #       待优化

    total_trade_amount = 0.0

    # 这个用来记录已经执行了交易
    frozen_fund = {}
    for myex in myex_list:
        frozen_fund[myex.name] = {
            # 进行交易而冻结的定价币
            'total_frozen_balance': 0.0,
            # 进行交易而冻结的商品币
            'total_frozen_stocks': 0.0,
        }

    for trade in sorted_list:
        buy_myex = trade['buy_myex']
        sell_myex = trade['sell_myex']
        buy_fee_ratio = buy_myex.trdfee['Buy'] / 100.0
        #sell_fee_ratio = sell_myex.trdfee['Sell'] / 100.0

        # 简单的排除检查，其实可以不需要
        if sell_myex.account['Stocks'] >= get_param('G_PARAM_MIN_TRADE_AMOUNT'):
            # 减掉之前交易冻结的资金
            balance = buy_myex.account['Balance'] - frozen_fund[buy_myex.name]['total_frozen_balance']
            stocks = sell_myex.account['Stocks'] - frozen_fund[sell_myex.name]['total_frozen_stocks']

            max_sell_amount = stocks
            # 必须算上手续费，否则可能出现错误结果
            max_buy_amount = balance / (trade['buy_price'] * (1.0 + buy_fee_ratio))
            max_trade_amount = min(max_buy_amount,
                                   max_sell_amount,
                                   trade['amount'])
            # 开始交易
            buy_order_id, sell_order_id, trade_amount = \
                    process_arbitrage_trade(trade, max_trade_amount)
            if not buy_order_id and not sell_order_id:
                # 很倒霉，这次套利交易因故不能执行，原因 process_arbitrage_trade 函数已经打印
                #LogDebug('该次套利交易因故不能执行：%s' % trade)
                continue
            if buy_order_id:
                frozen_fund[buy_myex.name]['total_frozen_balance'] += \
                        trade_amount * trade['buy_price'] * (1.0 + buy_fee_ratio)
            if sell_order_id:
                frozen_fund[sell_myex.name]['total_frozen_stocks'] += trade_amount

            if not buy_order_id or not sell_order_id:
                if buy_order_id:
                    Log('该次套利只成功下单买单，下单卖单失败，等待取消订单...')
                else:
                    Log('该次套利只成功下单卖单，下单买单失败，等待取消订单...')
                continue

            total_trade_amount += trade_amount

    return total_trade_amount

def clean_order_dict(myex, incompl_orders):
    '''
    只在字典里面保留 incompl_orders 存在的订单, 其他订单一律清理
    '''
    new_dict = {}
    for order in incompl_orders:
        oid = order['Id']
        if oid in myex.executed_orders:
            new_dict[oid] = myex.executed_orders[oid]
    myex.executed_orders = new_dict

def cancel_incompl_orders(myex_list):
    '''
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1

    ORDER_STATE_PENDING = 0
    ORDER_STATE_CLOSED = 1
    ORDER_STATE_CANCELED = 2

    只调用了 GetOrders() 获取信息

    @return
        未完成订单的总数
    '''
    incompl_order_count = 0
    for myex in myex_list:
        incompl_orders = myex.get_orders()
        if incompl_orders is None:
            Log('[%s] 获取所有未完成的订单失败' % myex.name)
            continue
        clean_order_dict(myex, incompl_orders)
        incompl_order_count += len(incompl_orders)
        if not incompl_orders:
            continue

        for order in incompl_orders:
            oid = order['Id']
            oinfo = myex.executed_orders.get(oid, {})
            # 对于刚下的订单, 至少等待 G_PARAM_WAIT_FOR_ORDER 个回合才会处理
            if oinfo.get('tick', 0) + get_param('G_PARAM_WAIT_FOR_ORDER') > get_loop_count():
                continue

            cancel_result = False
            try:
                # FIXME: 有些交易所的参数输入必须为字符串，有些则为数字
                # 返回操作结果，true表示取消订单请求发送成功，false取消订单请求
                # 发送失败（只是发送请求成功，交易所是否取消订单最好调用
                #           exchange.GetOrders() 查看）
                # 发送失败 - 肯定不能取消
                # 发送成功 - 不一定能取消，可能刚刚全部成交了（猜想）
                cancel_result = myex.cancel_order(order['Id'], oinfo.get('type', None))
            except:
                LogDebug(traceback.format_exc())
                Log('[%s] 未能取消未完成的订单：%s' % (myex.name, str(order['Id'])))
                Log('[%s] 请检查是否给予 API 取消交易订单的权限。' % myex.name)

            if not cancel_result:
                Log('[%s] 取消订单请求发送失败，Id = %s' % (myex.name, str(order['Id'])))
                continue
            touch_last_cancel_order_timestamp()

    return incompl_order_count

def _draw_table(*tables):
    global g_run_on_botvs
    if not tables:
        return

    if g_run_on_botvs:
        LogStatus('`' + '`\n`'.join(map(json.dumps, tables)) + '`')
        return

    import texttable
    prec = max(get_param('G_PARAM_PRICE_PREC'), get_param('G_PARAM_AMOUNT_PREC'))
    for table in tables:
        tab = texttable.Texttable(0)
        tab.set_precision(prec)

        header = []
        for i in table['cols']:
            if g_use_python3:
                header.append(i)
            else:
                header.append(i.decode('utf-8'))

        tab.header(header)
        align = ['l'] + ['c'] * (len(table['cols']) - 1)
        tab.set_cols_align(align)
        tab.set_cols_dtype(['t'] * len(table['cols']))
        tab.add_rows(table['rows'], header=False)
        Log('\n' + tab.draw())
    #Log('@' * 80)

def get_all_fund(myex_list):
    if not myex_list:
        return None

    all_fund = {
        'currency': '',
        # 冻结资金也算进去
        'balance': 0.0,
        'stocks': 0.0,
        # 平均价格
        'price': 0.0,
        'total': 0.0,

        # 原始信息
        'Balance': 0.0,
        'Stocks': 0.0,
        'FrozenBalance': 0.0,
        'FrozenStocks': 0.0,
    }

    alt_price = 0.0
    for myex in myex_list:
        all_fund['currency'] = myex.currency
        balance = myex.account['Balance'] + myex.account['FrozenBalance']
        stocks = myex.account['Stocks'] + myex.account['FrozenStocks']
        all_fund['balance'] += balance
        all_fund['stocks'] += stocks
        all_fund['total'] += balance + stocks * myex.ticker['Last']

        all_fund['Balance'] += myex.account['Balance']
        all_fund['FrozenBalance'] += myex.account['FrozenBalance']
        all_fund['Stocks'] += myex.account['Stocks']
        all_fund['FrozenStocks'] += myex.account['FrozenStocks']

        alt_price += myex.ticker['Last']

    avg_price = alt_price / len(myex_list)

    if all_fund['stocks'] != 0.0:
        all_fund['price'] = (all_fund['total'] - all_fund['balance']) / all_fund['stocks']
    else:
        all_fund['price'] = avg_price

    return all_fund

def refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms):
    global g_startup_time
    global g_real_arbit_diff
    if not myex_list:
        return

    tables = []
    # 显示的信息可以按照设置的精度显示，所以不保证显示的信息很准确
    price_prec = get_param('G_PARAM_PRICE_PREC')
    amount_prec = get_param('G_PARAM_AMOUNT_PREC')

    base = myex_list[0].base
    quote = myex_list[0].quote

    table_baseinfo = {
        'type': 'table',
        'title': '基础信息',
        'rows': [],
        'cols': [
            '开始时间',
            '当前时间',
            '交易对',
            '套利差(%)',
            '操作总延时(ms)',
        ]
    }
    row1 = [
        g_startup_time,
        get_strtime(),
        '%s/%s' % (base, quote),
        '%.4f' % g_real_arbit_diff,
        '%.1f' % op_delay_ms,
    ]
    assert len(table_baseinfo['cols']) == len(row1)
    table_baseinfo['rows'].append(row1)

    # 概要信息
    table_summary = {
        'type': 'table',
        'title': '综合信息',
        'cols': [
            '可用%s' % base,
            '冻结%s' % base,
            '可用%s' % quote,
            '冻结%s' % quote,
            '均价(%s)' % quote,
            '变化(%)',

            # 市值用最后成交价计算
            '市值(%s)' % quote,

            '套利(%s)' % quote,
            #'套利收益率(%)',
            '收益(%s)' % quote,
            '收益率(%)'
        ],
        'rows': [],
    }

    # 初始信息
    row1 = [
        '%.*f' % (amount_prec, all_init_fund['Stocks']),
        '%.*f' % (amount_prec, all_init_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_init_fund['Balance']),
        '%.*f' % (price_prec, all_init_fund['FrozenBalance']),
        '%.*f' % (price_prec, all_init_fund['price']),
        '%.*f' % (4, 0.0),

        '%.*f' % (price_prec, all_init_fund['total']),

        'N/A',
        #'N/A',
        'N/A',
        'N/A',
    ]

    total_profit = all_curr_fund['total'] - all_init_fund['total']
    row2 = [
        '%.*f' % (amount_prec, all_curr_fund['Stocks']),
        '%.*f' % (amount_prec, all_curr_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_curr_fund['Balance']),
        '%.*f' % (price_prec, all_curr_fund['FrozenBalance']),
        '%.*f' % (price_prec, all_curr_fund['price']),
        '%.*f' % (4, all_curr_fund['price']/all_init_fund['price']*100.0-100.0),

        '%.*f' % (price_prec, all_curr_fund['total']),

        '%.*f' % (price_prec, get_stats('STATS_ARBITRAGE_PROFIT')),
        #'%.*f' % (4, get_stats('STATS_ARBITRAGE_PROFIT') / all_curr_fund['total']),
        '%.*f' % (price_prec, total_profit),
        '%.*f' % (4, total_profit / all_init_fund['total'] * 100),
    ]

    assert len(table_summary['cols']) == len(row1)
    assert len(table_summary['cols']) == len(row2)
    table_summary['rows'].append(row1)
    table_summary['rows'].append(row2)

    table_exchange_summary = {
        'type': 'table',
        'title': '交易所概要信息',
        # headers
        'cols': [
            '交易所',
            'API模式',
            '延时(ms)',

            '买1价',
            '卖1价',
            #'最后成交价',
            '现价',

            '可用%s' % base,
            '冻结%s' % base,
            '可用%s' % quote,
            '冻结%s' % quote,

            '可购%s' % base,
            '手续费(%)',
        ],
        'rows': [],
    }

    for myex in myex_list:
        try:
            # NOTE: 可购量用 卖1 价格计算
            max_buy_amount_mesg = '%.*f' % (myex.amount_prec,
                                            myex.account['Balance'] / myex.ticker['Sell'])
        except ZeroDivisionError:
            max_buy_amount_mesg = 'N/A'
        row = [
            myex.name,
            myex.api_mode,
            '%.1f' % myex.delay,

            '%.*f' % (price_prec, myex.ticker['Buy']),
            '%.*f' % (price_prec, myex.ticker['Sell']),
            '%.*f' % (price_prec, myex.ticker['Last']),

            '%.*f' % (amount_prec, myex.account['Stocks']),
            '%.*f' % (amount_prec, myex.account['FrozenStocks']),
            '%.*f' % (price_prec, myex.account['Balance']),
            '%.*f' % (price_prec, myex.account['FrozenBalance']),

            max_buy_amount_mesg,
            '买 %.2f, 卖 %.2f' % (myex.trdfee['Buy'], myex.trdfee['Sell']),
        ]
        assert len(table_exchange_summary['cols']) == len(row)
        table_exchange_summary['rows'].append(row)

    tables.append(table_baseinfo)
    tables.append(table_summary)
    tables.append(table_exchange_summary)
    _draw_table(*tables)

# ============================================================
### 主要流程
#       - 取消未完成订单
#       - 套利
#
# 亏损唯一来源: 套利订单未成交  (1)
# 套利终止原因: 只能单向套利    (2)
def mainloop(all_init_fund, myex_list):
    global g_loop_count
    # 循环间隔，单位毫秒
    loop_interval = get_param('G_PARAM_LOOP_INTERVAL')

    myex_comp_list = generate_compare_list(myex_list)

    # 这样可以保证第一次进入循环不睡眠
    prev_loop_time = 0.0
    while True:
        g_loop_count += 1
        loop_count = g_loop_count

        # 本轮是否已经工作了? 取消未完成订单, 套利, 平仓都称为工作
        worked = False

        # @ 保持每次循环持续时间为 loop_interval，如果循环时间过长，不睡眠
        curr_loop_time = time.time()
        loop_time_diff_ms = (curr_loop_time - prev_loop_time) * 1000.0
        if loop_time_diff_ms < loop_interval:
            if not is_emutest_mode():
                Sleep(loop_interval - loop_time_diff_ms)

        prev_loop_time = time.time()
        # @ 优化 account 获取，如果改变账号的操作的话，立即切换为随机刷新
        # FIXME 刚刚挂单, 但是没有立即完成, 那么在订单完成之前都要刷新 account
        #       这会稍微影响套利交易量而影响收益率
        # TODO: 处理交易所出错的情况，需要冻结交易所一段时间
        if loop_count % 60 == 1:
            for myex in myex_list:
                if myex.account_refresh_state == 'refresh_complete':
                    myex.account_refresh_state = 'refresh_random'

        # @ 模拟测试获取新数据或者退出
        if is_emutest_mode() and loop_count > 1:
            exit = False
            for myex in myex_list:
                # TODO: 支持获取空结果，但是返回 None 的话表示结束
                if not myex.botvs_exchange._get_new_record():
                    exit = True
                    break
            if exit:
                all_curr_fund = get_all_fund(myex_list)
                refresh_status(myex_list, all_curr_fund, all_init_fund, 0.0)
                Log('End in loop', loop_count)
                break

        # @ 取消未完成的订单, 取消订单不需要最新的 account, ticker, depth
        if loop_count % 90 == 0:
            cancel_incompl_orders(myex_list)
            if get_last_cancel_order_timestamp() == loop_count:
                worked = True

        # @ 刷新交易所数据
        clean_exchange_data(myex_list, loop_count)  # 暂时只清理深度和延时数据
        # 获取 account, ticker, depth
        fetch_exchange_data(myex_list, myex_comp_list, loop_count)

        # @ 进行套利
        if loop_count % 3600 == 1:
            Log('正在观察大盘，如果监测到有利差，'
                + '将开始套利。当前轮询次数为：%d' % loop_count)
        all_trade_list = []
        # 在模拟测试模式，得到套利机会后要等待若干回合，
        # 否则可能反复打印同样的套利交易
        if is_emutest_mode() and \
           loop_count <= (get_last_arbitrage_timestamp() + 1 \
                    + get_param('G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE')):
            pass
        # 只有在本轮没有执行过重试交易和趋势平仓交易时，才尝试套利
        elif not worked:
            all_trade_list = make_arbit_trades(myex_comp_list)
        # 处理这些可能套利的订单
        ret = process_arbitrage_trades(myex_list, all_trade_list)
        if ret:
            worked = True
            if is_debug_mode():
                LogDebug('策略计算所得套利订单为：%s'
                         % json.dumps(norm4json(all_trade_list),
                                      indent=None, sort_keys=True))

        # @ 刷新状态信息
        op_delay_ms = (time.time() - prev_loop_time) * 1000.0
        all_curr_fund = get_all_fund(myex_list)
        if is_emutest_mode():
            if loop_count % 3600 == 0:
                refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms)
        else:
            refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms)

def currency_to_base_quote(currency):
    '''
    BTC_USDT -> BTC, USDT
    '''
    li = currency.split('_')
    if (len(li) >= 2):
        return li[0], li[1]
    else:
        return li[0], ''

def main(argv=None):
    global g_myex_list
    global g_all_init_fund
    global exchanges
    global g_startup_time
    g_startup_time = get_strtime()
    Log('策略开始运行于：%s' % g_startup_time)
    if len(exchanges) < 2:
        Log('少于 2 个交易所是不能运行此策略的。')
        return -1
    elif len(exchanges) > 50:
        Log('大于 50 个交易所是不能运行此策略的。')
        return -1

    websocket_exchanges = {
        'Binance',
        'Huobi',
        'OKEX',
    }

    # 初始总资金
    all_init_fund = {
        'currency': '',
        # 冻结资金也算进去
        'balance': 0.0,
        'stocks': 0.0,
        # 这为平均价格
        'price': 0.0,
        'total': 0.0,

        # 原始信息
        'Balance': 0.0,
        'Stocks': 0.0,
        'FrozenBalance': 0.0,
        'FrozenStocks': 0.0,
    }
    g_all_init_fund = all_init_fund

    fee_list = get_param('G_PARAM_TRADE_FEE').strip().split(',')
    fee_list = [e.strip() for e in fee_list]

    myex_list = []
    alt_price = 0.0
    for idx, ex in enumerate(exchanges):
        if is_emutest_mode():
            ex._init_ExchangeRecords()
            ex._get_new_record()
            ex._set_account(Balance=get_param('G_PARAM_EMU_BALANCE'),
                            Stocks=get_param('G_PARAM_EMU_STOCKS'))

        myex = MyExchange(ex)
        myex_list.append(myex)

        # 设置自定义的手续费
        try:
            buy_fee = fee_list[idx*2]
            sell_fee = fee_list[idx*2+1]
            if buy_fee:
                myex.set_trade_fee(buy_fee=float(buy_fee))
            if sell_fee:
                myex.set_trade_fee(sell_fee=float(sell_fee))
        except IndexError:
            pass
        except:
            Log('交易手续费参数错误："%s"' % get_param('G_PARAM_TRADE_FEE'))
            Log(traceback.format_exc())
            return -1
        if is_emutest_mode():
            ex._set_trade_fee(myex.trdfee['Buy'], myex.trdfee['Sell'])

        # 处理 websocket 模式
        if get_param('G_PARAM_USE_WEBSOCKET'):
            if myex.name in websocket_exchanges:
                ret = myex.botvs_exchange.IO('websocket')
                if ret:
                    # 立即返回模式, 如果当前还没有接收到交易所最新的行情数据推送, 
                    # 就立即返回旧的行情数据,如果有新的数据就返回新的数据
                    myex.botvs_exchange.IO("mode", 0)
                    myex.api_mode = 'websocket'
                    LogDebug("[%s] 的 API 模式为 %s" % (myex.name, myex.api_mode))

        this_balance = myex.account['Balance'] + myex.account['FrozenBalance']
        this_stocks = myex.account['Stocks'] + myex.account['FrozenStocks']
        all_init_fund['balance'] += this_balance
        all_init_fund['stocks'] += this_stocks
        all_init_fund['total'] += this_balance + this_stocks * myex.ticker['Last']

        all_init_fund['Balance'] += myex.account['Balance']
        all_init_fund['FrozenBalance'] += myex.account['FrozenBalance']
        all_init_fund['Stocks'] += myex.account['Stocks']
        all_init_fund['FrozenStocks'] += myex.account['FrozenStocks']

        alt_price += myex.ticker['Last']

    g_myex_list = myex_list
    avg_price = alt_price / len(myex_list)

    # 定价币别名，有些定价币基本等值的，这些情况需要支持，例如 USD 和 USDT
    quote_alias = {
        'USD': 'USDT',
    }

    # 检查交易对是否一致，不一致不能继续
    # USDT 和 USD 一致
    for i in range(len(myex_list) - 1):
        aex = myex_list[0]
        bex = myex_list[i+1]
        aquote = quote_alias.get(aex.quote, aex.quote)
        bquote = quote_alias.get(bex.quote, bex.quote)
        if aquote == 'USD': aquote = 'USDT'
        if bquote == 'USD': bquote = 'USDT'
        if aex.base != bex.base or aquote != bquote:
            Log('[%s] 的交易对为 %s，而 [%s] 的交易对为 %s，交易对不一致不能运行策略。'
                % (aex.name, aex.currency, bex.name, bex.currency))
            return -1

    if all_init_fund['total'] <= 0.0:
        Log('初始仓位没有资金，无法运行策略，请建仓后重试。')
        return -1
    if all_init_fund['stocks'] <= 0.0:
        Log('初始仓位的商品币为 0.0，无法运行策略，请调整仓位后重试。')
        return -1

    all_init_fund['currency'] = myex_list[0].currency
    if all_init_fund['stocks'] != 0.0:
        all_init_fund['price'] = (all_init_fund['total'] -
                                  all_init_fund['balance']) / all_init_fund['stocks']
    else:
        all_init_fund['price'] = avg_price

    # 开始主循环
    try:
        mainloop(all_init_fund, myex_list)
    except KeyboardInterrupt:
        pass
    except:
        Log("发生了意外错误，请把错误信息保存并提交给作者以分析错误原因！")
        Log(traceback.format_exc())

if __name__ == '__main__':
    sys.exit(main(sys.argv))
