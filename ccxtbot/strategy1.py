#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''backtest
start: 2018-01-11 00:00:00
end: 2018-01-12 22:00:00
period: 5m
exchanges: [{"eid":"Bitfinex","currency":"BTC","balance":100,"stocks":101},{"eid":"OKEX","currency":"LTC_BTC","balance":102,"stocks":103},{"eid":"Huobi","currency":"LTC_BTC","balance":104,"stocks":105}]
'''
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

# TODO
# [X] 支持模拟交易模式
# [ ] trend_machine() 函数逻辑修正
# [ ] 处理下单失败的情况，尤其是套利下单
# [ ] 有些交易所有频率限制，需要处理这种情况 (Quoinex，300次/5分钟)
# [ ] 异步优化

# ==================== 以上处理模块 ====================

g_startup_time = ''
g_run_on_botvs = True

# 这个可以作为时间戳，策略的时间戳精度即为轮询间隔
g_loop_count = 0
# 最后一次下单的时间戳，无论什么方式的下单都更新，如 套利，重试(backup)，平仓
g_last_order_timestamp = 0
# 最后一次取消订单的时间戳
g_last_cancel_order_timestamp = 0
# 最后一次进行套利交易的时间戳
g_last_arbitrage_timestamp = 0

# 统计信息，理论上这些统计信息都是只能加不能减的
g_stats = {
    # 套利数量，一轮套利，例买30卖30，只算一次30
    'STATS_ARBITRAGE_AMOUNT': 0.0,
    # 执行套利交易的次数
    'STATS_ARBITRAGE_COUNT': 0,
    # 套利收益，这是成功套利后的收益，也就是买和卖都成交后计算的差价收益
    # 如果在一次买卖套利当中，买卖成交量不相等，只能计算买/卖最小成交量为套利收益
    # 未能成交部分，额，暂时不知道算到哪里，只能算是一次套利失败后的常规成交单
    # 这部分成交量统计到交易所的总共成交量里面
    'STATS_ARBITRAGE_PROFIT': 0.0,
}

# 全部的脚本参数的默认值
ALL_PARAMETERS = {
    # 模拟测试模式，即用历史数据测试，无需实时获取信息来测试
    # 模拟测试模式必须和模拟模式一起用
    'G_PARAM_EMUTEST_MODE': True,

    # 是否使用模拟模式
    # 模拟交易模式，即所有交易都是模拟的，不是实际连接到交易所交易
    'G_PARAM_EMU_MODE': True,
    # 模拟模式的账号余额，实盘模式会忽略此参数
    'G_PARAM_EMU_BALANCE': 0.15,
    # 模拟模式的账号余币，实盘模式会忽略此参数
    'G_PARAM_EMU_STOCKS': 20,
    # 模拟模式进行套利交易后，暂停检测套利的轮询次数
    # 因为模拟模式的交易不影响市场，所以如果套利后不暂停，
    # 可能会马上再进行同样的套利，虽然会受余额限制。
    # 不暂停就设置为 0
    'G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE': 10,

    # 下单后等待多久(轮询次数)才检查未完成的订单
    'G_PARAM_WAIT_FOR_ORDER': 10,

    # TODO
    # 存档名称。空字符串表示不开启存档功能
    'G_PARAM_SAVE_FILE_NAME': 'test.sav',

    # 是否需要从存档读取初始信息来执行策略
    'G_PARAM_INIT_FROM_SAVE': False,

    # 是否优先使用 websocket 模式
    # 一般 websocket 提供更好的实时性，但不是每个交易所都支持
    'G_PARAM_USE_WEBSOCKET': True,

    # 轮询间隔，毫秒
    'G_PARAM_LOOP_INTERVAL': 5000,

    # true 则是手续费基础上再加套利差，否则是直接套利差
    # TODO
    "TODO": True,

    # 套利差，百分率
    # 这是策略的套利差，实际使用的时候会经常根据观察的行情来更新
    # 使用场景：
    #   - 计算套利交易时，和交易费率一起算作基本交易成本
    'G_PARAM_ARBITRAGE_DIFFERENCE': 0.25,
    # 套利差下限
    'G_PARAM_ARBITRAGE_DIFFERENCE_MIN': 0.2,
    # 套利差上限
    'G_PARAM_ARBITRAGE_DIFFERENCE_MAX': 1.2,

    # 一般设置为每次套利的基本成交数量
    # 这个参数作为以下的调整依据：
    #   - 根据最近套利交易量和这个数值对比，微调套利差
    #   - 套利时，以此为基础乘以一个策略系数得出策略目标交易数量
    'G_PARAM_BASE_TRADE_AMOUNT': 5,

    # 每单的最少交易量
    # 这个一般根据交易所的限制设置，如有些交易所对某些币有最小交易量限制的话
    'G_PARAM_MIN_TRADE_AMOUNT': 1,

    # 增强学习次数（这个轮询次数后开始套利）
    'G_PARAM_BOOST_LEARN_COUNT': 500,

    # 首次调整价格差价时的调整参数，百分率
    # 即首次计算价格差时，对这个价格差的接受程度
    # 建议 10，波动大的币种可以设定大一些。这个值越大，
    # 初始学习周期理论上来说需时就越小。只发挥一次作用。
    'G_PARAM_DELTA_PARAM': 65,

    # 滑点，根据设置的币种设置，不然会有灾难性后果！
    # 为了快速成交，买卖时需要额外付出的价格，最小可设置为 0.0
    # TODO: 需要严格检查这个参数, 因为设置不当会有灾难性后果
    # 滑点只在套利计算时才考虑，其他的“平仓交易”， “取消再补充交易”都不考虑
    'G_PARAM_SLIP_POINT': 0.000002,

    # 所谓的 beta 石，暂时不理解
    'G_PARAM_TRADE_AMOUNT_MAGIC': 700,

    # 平仓方式
    #   - 0 为按照轮询次数（可根据轮询间隔换算为时间）调仓，
    #   - 1 为按照搬砖量（交易量）调仓
    #   - 2 为按照上一次搬砖后到现在的轮询次数（时间）
    # 有观点为：好的交易所建议按照搬砖量，差的按照轮询次数
    'G_PARAM_TRANSFER_POSITION_MODE': 0,

    # 趋势机阈值
    # 这个阈值是用来判断是否需要趋势平仓的，
    # 趋势机启动前至少要轮询这次数和增强学习次数之和
    'G_PARAM_TREND_MACHINE_THRESHOLD': 40,

    # 保留多少的百分比的商品币用来同步趋势机
    # 平仓时，如果需要买入，则会多买入这个比例的商品币
    # 平仓时，如果需要卖出，则会多卖出这个比例的商品币
    # 假设为 10，则平仓是理想状态为
    #   1 : 1
    # 平仓买入时，根据这个参数修正为
    #   0.8 : 1.2 -> 1.1 : 0.9
    # 平仓卖出时，根据这个参数修正为
    #   1.2 : 0.8 -> 0.9 : 1.1
    # 这可以理解为平仓仓位偏置率
    'G_PARAM_TREND_FUND_PERCENT': 1,

    # 平仓方式
    # True 为直接等分平仓
    # False 为严格按照初始状态平仓（需要存档支持）
    # TODO
    'TODO x': True,

    # 这个勾上以后会按实际值计算交易费率，否则是理论值。
    'G_PARAM_COUNT_REAL_FEE': True,

    # 最大差价
    # 这个对差价过大的交易所作调整用的，设置为你看到过的交易所间的最大差价。
    'G_PARAM_MAX_DIFF': 0.00005,

    # 趋势平仓时，判断套利差时的系数(直接相乘)，只在趋势平仓是才使用
    # 这可以额外控制平仓时的套利差，例如需要平仓时不考虑套利差就填 0.0
    'G_PARAM_TREND_ARBITRAGE_DIFFERENCE_FACTOR': 2.0,

    # 计算套利时，是否忽略交易手续费？
    # 计算套利时，一般可以认为差价必须大于 (买手续费 + 卖手续费 + 套利差) 才可以套利
    # 如果忽略手续费的话，直接使用套利差来计算，这时候套利差的设置必须考虑手续费率
    # 这个选项一般不需要导出，使用默认值即可
    'G_PARAM_IGNORE_TRADE_FEE': False,

    # NOTE: 这是自定义的精度
    #   - 只在最后执行买/卖时才会按照这个精度截断价格/交易数量
    #   - 只在记录买/卖价格/交易数量时，才截断数值
    # 其他时候直接使用python的float数据结构（总计17位的精度）
    # 价格精度，小数点后位数
    'G_PARAM_PRICE_PREC': 6,

    # NOTE: 同上
    # 交易数量精度，小数点后位数
    'G_PARAM_AMOUNT_PREC': 2,

    # 学习速度，值越大学习越快，可取值范围 1-4
    # 具体为调整 delta 的速率
    # 对于变动慢的，就选低档，对于变动块的，比如无手续费小波段套利，就选高档
    'G_PARAM_LEARN_SPEED': 2,

    # 最大的统一精度，一般取为所有交易所中精度最大的值
    # 现在所知为 8，因为 BTC 的最小单位“聪”即为 8 位小数精度
    'G_PARAM_MAX_UNIFY_PREC': 8,
}

def get_param(name, default=None):
    '''获取策略参数'''
    global ALL_PARAMETERS
    try:
        exec('global %s' % name)
        return eval(name)
    except NameError:
        return ALL_PARAMETERS.get(name, default)

try:
    exchanges
except NameError:
    g_run_on_botvs = False
    if get_param('G_PARAM_EMUTEST_MODE') and get_param('G_PARAM_EMUTEST_MODE'):
        from emutest import *
    else:
        from botvs import *

# 实际的套利差，因为这个要经常更新
g_real_abtr_diff = get_param('G_PARAM_ARBITRAGE_DIFFERENCE')

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

def minus_stats(key, val):
    global g_stats
    g_stats[key] -= val

def get_stats(key):
    global g_stats
    return g_stats.get(key)

def is_emulate_mode():
    '''
    - 返回的 account 为固定值
    - 买卖一定成功
    - 每次买卖后，下次更新account，直接从上次的买卖数据计算
    - 其他和 viewer 一样
    '''
    return get_param('G_PARAM_EMU_MODE')

def is_emutest_mode():
    '''
    用数据库的历史记录模拟测试
    '''
    return get_param('G_PARAM_EMUTEST_MODE', True) and is_emulate_mode()

def get_loop_count():
    global g_loop_count
    return g_loop_count

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
        import pytz
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

class MyExchange(object):
    def __init__(self, botvs_exchange):
        global TRDFEE_DICT
        self.botvs_exchange = botvs_exchange
        self.born_time = time.time()

        self.currency = bytes2str(self.botvs_exchange.GetCurrency())
        self.base, self.quote = currency_to_base_quote(self.currency)

        # 这两个信息只要一次获取即可
        self.name = bytes2str(self.botvs_exchange.GetName())
        self.trdfee = TRDFEE_DICT.get(self.name.lower(), DEFAULT_TRDFEE)

        # 精度，一般交易所的精度都是小数点后 8 位
        self.price_prec = get_param('G_PARAM_PRICE_PREC')
        self.amount_prec = get_param('G_PARAM_AMOUNT_PREC')

        ### ========== 以上属性只读 ==========

        # 这三个信息是要经常刷新的
        self.account = bytes2str(self.botvs_exchange.GetAccount())
        if not self.account:
            # 初始化的时候，可以重试一次
            self.account = bytes2str(self.botvs_exchange.GetAccount())
        self.ticker = bytes2str(self.botvs_exchange.GetTicker())
        if not self.ticker:
            # 初始化的时候，可以重试一次
            self.ticker = bytes2str(self.botvs_exchange.GetTicker())
        self.depth = None

        # 这里使用的 timestamp 为轮询滴答，亦即，循环次数
        self.account_timestamp = 0
        self.ticker_timestamp = 0
        self.depth_timestamp = 0

        self.init_balance = self.account['Balance']
        self.init_stock = self.account['Stocks']

        self.init_last_price = self.ticker['Last']

        # 现在一般为 'REST' 或者 'websocket'
        self.api_mode = 'REST' # 默认为 'REST'
        self.delay = 0.0

        # 'refresh_instant'     - 立即刷新
        # 'refresh_random'      - 随机刷新
        # 'refresh_complete'    - 刷新完成
        # 因为一般交易所的api实现用，获取account信息延时都比较大，
        # 并且，如果没有发生交易，account的状态理论上是不变的
        # 所以刷新account需要优化
        #   - 只有执行交易操作后，才需要刷新account
        #   - 观察的时候，轮询N次后才刷新一次
        self.account_refresh_state = 'refresh_instant'

        # 对另一个交易所的delta值
        self.delta_dict = {}
        # 对另一个交易所的delta_magic值
        # exname: {'times': 0, 'diffs': 0.0}
        self.delta_magic = {}

        self.last_buy_price = 0.0
        self.last_sell_price = 0.0

        # 例如 Quoinex 的频率限制为 300次/5分钟，则前者为 300，后者为 300
        # 指定时间内 api 请求数量，如果 < 0，表示无限制
        self.rate_limit_times_per_period = 5
        # 指定的单位时间，单位秒
        self.rate_limit_period = 1.0
        # 本轮频率计数
        self.rate_limit_times = 0
        # 本轮频率计数开始的时间
        self.rate_limit_t0 = 0.0

        # 记录套利的交易单，下单时填充，完成时清除
        # {order_id: {'price': x, 'amount': x}, ...}
        self.arbitrage_buy_orders = {}
        self.arbitrage_sell_orders = {}

        self.trend_buy_orders = {}
        self.trend_sell_orders = {}

        self.backup_buy_orders = {}
        self.backup_sell_orders = {}

        ### NOTE
        ### 下面的交易量统计信息都是在本策略下单时统计的，如果发生了取消未完成的订单，
        ### 那么这些统计信息都是不准确的，暂时无法做到绝对准确
        ### 绝对准确需要访问交易所获取确切的交易量，但是这无法区分这些交易量是用来
        ### 套利还是平仓的

        # 统计趋势机执行的买卖单交易量
        self.stats_trend_buy_amount = 0.0
        self.stats_trend_sell_amount = 0.0

        # 统计套利交易量
        self.stats_arbitrage_buy_amount = 0.0
        self.stats_arbitrage_sell_amount = 0.0

        # 统计总共的交易量，不管你是用于趋势还是用于套利的
        self.stats_total_buy_amount = 0.0
        self.stats_total_sell_amount = 0.0

        # 用于模拟交易模式
        self.account_diffs = []

    def clean_data(self):
        '''仅清空延时和深度'''
        self.depth = None
        self.delay = 0.0

    def touch_rate_limit(self):
        now = time.time()
        diff = now - self.rate_limit_t0
        if diff >= self.rate_limit_period:
            self.rate_limit_t0 = now
            self.rate_limit_times = 0
        self.rate_limit_times += 1

    def check_rate_limit(self, times=1):
        '''
        根据频率限制以及当前频率计数，返回本次轮询能否执行 API 访问
        '''
        now = time.time()
        diff = now - self.rate_limit_t0
        alt_times = self.rate_limit_times + times
        if diff < self.rate_limit_period and alt_times < self.rate_limit_times_per_period:
            return True
        # TODO 不好写

    def buy(self, price, amount):
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        prec = get_param('G_PARAM_MAX_UNIFY_PREC')
        # FIXME: 'Zaif' 交易所据说会发生异常情况
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        Log('[%s] buy(price=%.*f, amount=%.*f)'
            % (self.name, self.price_prec, price, self.amount_prec, amount))
        oid = self.botvs_exchange.Buy(float_round_down(price, self.price_prec),
                                      float_round_down(amount, self.amount_prec))
        return bytes2str(oid)

    def sell(self, price, amount):
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        prec = get_param('G_PARAM_MAX_UNIFY_PREC')
        # FIXME: 'Zaif' 交易所据说会发生异常情况
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        Log('[%s] sell(price=%.*f, amount=%.*f)'
            % (self.name, self.price_prec, price, self.amount_prec, amount))
        oid = self.botvs_exchange.Sell(float_round_down(price, self.price_prec),
                                       float_round_down(amount, self.amount_prec))
        return bytes2str(oid)

    def get_account(self):
        account = bytes2str(self.botvs_exchange.GetAccount())
        if account is None:
            LogError('[%s] 获取 Account 数据失败' % self.name)
            return None
        self.account = account
        self.account_refresh_state = 'refresh_complete'
        return self.account

    def get_ticker(self):
        ticker = bytes2str(self.botvs_exchange.GetTicker())
        if ticker is None:
            LogError('[%s] 获取 Ticker 数据失败' % self.name)
            return None
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
        return bytes2str(self.botvs_exchange.GetOrders())

    def cancel_order(self, oid):
        return self.botvs_exchange.CancelOrder(oid)

    def init_delta(self, myex_b):
        # 首次对差价进行系数修正，以提高套现效率和成交率
        diff = self.ticker['Last'] - myex_b.ticker['Last']
        diff_abs = abs(diff)

        # 需要对差价进行一个系数的微调，效果是经验值...
        max_diff = abs(get_param('G_PARAM_MAX_DIFF'))
        # 开始的时候对差价的接受程度
        delta_param = get_param('G_PARAM_DELTA_PARAM')
        if diff_abs < max_diff * 0.3:   # 需要缩小
            delta_xx = 0.2 * delta_param
        elif diff_abs < max_diff * 0.7: # 需要缩小
            delta_xx = 0.5 * delta_param
        else:
            delta_xx = delta_param

        self.delta_dict[myex_b.name] = diff * delta_xx / 100.0
        self.delta_magic[myex_b.name] = {
            # 累计的次数
            'times': 0,
            # 累计的diff，为 a - b，可为负数
            'diffs': 0,
        }

    def tune_delta(self, myex_b):
        '''
        差价累计学习
        根据双方的 ticker 的最后成交价的差值，更新 delta

        最终目的就是调整 delta_dict[exb_name] 的值
        一经调整 delta_dict[exb_name] 即重置 delta_magic
        '''
        a = self
        b = myex_b
        prec = get_param('G_PARAM_MAX_UNIFY_PREC')

        last_price_diff = a.ticker['Last'] - b.ticker['Last']

        # 累计学习差价20次后，根据学习速度调整 delta_dict (delta) 的值
        # delta_magic 是用来存储差价历史的
        delta_magic = self.delta_magic[b.name]
        delta_magic['diffs'] += last_price_diff
        delta_magic['times'] += 1

        # 开始微调
        learn_speed = get_param('G_PARAM_LEARN_SPEED')
        if delta_magic['times'] >= 20:
            if learn_speed == 1:    # 0.99999
                p0 = 0.9998
                p1 = 0.00019
            elif learn_speed == 2:  # 0.99998
                p0 = 0.9995
                p1 = 0.00048
            elif learn_speed == 3:  # 0.99998
                p0 = 0.998
                p1 = 0.0018
            elif learn_speed == 4:  # 0.99998
                p0 = 0.997
                p1 = 0.0028
            else:
                p0 = 0.5
                p1 = 0.5
                LogError('“学习速度”参数错误：%d' % learn_speed)

            # NOTE: 这里应该使用 'times' 的值，否则肯定错的吧
            diff_avg = self.delta_magic[b.name]['diffs'] / self.delta_magic[b.name]['times']
            prev_delta = self.delta_dict[b.name]
            # 最终目的就是调整 delta_dict[b.name] 的值
            # 根据以上逻辑得知，如果差价一直保持不变，
            # 策略的 delta 会以 0.00001 到 0.00002 的比例缩小（每20次循环）
            self.delta_dict[b.name] = self.delta_dict[b.name] * p0 + \
                                        diff_avg * p1
            #if get_loop_count() % 1000 == 0:
            #LogDebug('loop %d 最近学习到的差价为 %.*f，更新 delta (%s - %s)：%.*f -> %.*f'
            #         % (get_loop_count(), prec, diff_avg,
            #            a.name, b.name,
            #            prec, prev_delta,
            #            prec, self.delta_dict[b.name]))
            # 重置
            delta_magic['times'] = 0
            delta_magic['diffs'] = 0

        return self.delta_dict[b.name]

    def _make_trade_comp_exchange(self, myex_b, slip_point=0.0):
        '''
        根据当前买1卖1的挂单计算套利交易
        '''
        a = self
        b = myex_b

        # NOTE: 更新 depth 也是根据 caculate_arbitrage 返回结果决定的
        #   	所以这里可以确定 depth 的访问不出问题
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

    def make_trade_comp_exchange(self, myex_b, slip_point=0.0):
        prec = get_param('G_PARAM_MAX_UNIFY_PREC')
        trade = self._make_trade_comp_exchange(myex_b, slip_point=slip_point)
        if not trade:
            return None

        buy_myex = trade['buy_myex']
        sell_myex = trade['sell_myex']
        delta = trade['delta']

        min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
        if sell_myex.account['Stocks'] > (buy_myex.account['Stocks'] + min_trade_amount) * 8:
            # 卖单的交易所的商品币比买单的交易所的商品币多太多了（8倍以上）
            # 卖单的量可以提高
            strategy_amount = (sell_myex.account['Stocks'] - buy_myex.account['Stocks']) * 0.6
            LogDebug('交易数量需要扩大：%.*f -> %.*f' %
                     (prec, trade['amount'], prec, strategy_amount))
        else:
            diff = trade['sell_price'] - trade['buy_price'] - delta
            # beta石。这个用来限制每次交易量的变动
            # 建议设置1000，这个数字越大，成交越快，越小成交单拆分越多。
            trade_amount_magic = get_param('G_PARAM_TRADE_AMOUNT_MAGIC')
            # TODO: 理解含义
            param = diff / ( abs(delta) + trade['buy_price'] /  trade_amount_magic )
            strategy_amount = get_param('G_PARAM_BASE_TRADE_AMOUNT') * param

        max_sell_amount = sell_myex.account['Stocks']
        max_buy_amount = float_round_down(float(buy_myex.account['Balance']) / trade['buy_price'], prec)
        min_in_three = min(max_sell_amount, max_buy_amount, trade['amount'])
        if strategy_amount < min_trade_amount:
            strategy_amount = min_trade_amount
        if strategy_amount > min_in_three:
            strategy_amount = min_in_three

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
                        buy_price, buy_fee,
                        delta_sell2buy):
    '''
    比较两个交易所的差价
    last_buy_price 为 a 和 b 交易所最后成交价的差价
    sell_price 为卖单交易所的卖价格，一般为订单薄的买1价
    sell_fee 百分率
    buy_price 为买单交易所的买价格，一般为订单薄的卖1价
    buy_fee 百分率

    delta_sell2buy 此为 (卖单交易所 - 买单交易所) 的 delta，注意符号
    '''
    global g_real_abtr_diff
    max_diff = abs(get_param('G_PARAM_MAX_DIFF'))
    alt_abtr_diff_percent = g_real_abtr_diff

    # 如果当前最后成交差价达到了最大差价的 70% 以上，可以扩大套利差
    if abs(last_price_diff) > max_diff * 0.7:
        ratio = abs(last_price_diff) / max_diff
        alt_abtr_diff_percent += ratio * alt_abtr_diff_percent

    buy_fee_ratio = buy_fee / 100.0
    sell_fee_ratio = sell_fee / 100.0
    # NOTE: 把套利差算到费率那里，其实是指每次套利必须至少获取此比例的利润
    fee_ratio = alt_abtr_diff_percent / 100.0
    # 计算套利时，可以忽略交易的手续费，这只在有特殊需要的时候才使用
    if not get_param('G_PARAM_IGNORE_TRADE_FEE'):
        # 假设交易量一样的话，正确的公式为：
        # s - b - s*fee_sell - b*fee_buy
        # 这是原版，仅作参考
        #fee_ratio += sell_fee_ratio + buy_fee_ratio
        #price_diff = sell_price - buy_price - (buy_price * fee_ratio) - delta_sell2buy
        # ----------------------------------------
        #fee = sell_fee + buy_fee + alt_abtr_diff_percent
        #price_diff = sell_price - buy_price * (1 + fee * 1.0/ 100) - delta_sell2buy
        # ========================================
        price_diff = sell_price - buy_price \
                   - sell_price * sell_fee_ratio \
                   - buy_price * buy_fee_ratio \
                   - buy_price * fee_ratio \
                   - delta_sell2buy
    else:
        price_diff = sell_price - buy_price \
                   - buy_price * fee_ratio \
                   - delta_sell2buy


    return price_diff

def caculate_arbitrage(myex_a, myex_b, slip_point=0.0):
    '''
    根据当前买1卖1的挂单计算套利交易
    把“滑点”也考虑了
    '''
    result = {}

    a = myex_a
    b = myex_b

    delta = a.delta_dict[b.name]

    a_sell_price = a.ticker['Buy'] - slip_point
    a_buy_price = a.ticker['Sell'] + slip_point

    b_sell_price = b.ticker['Buy'] - slip_point
    b_buy_price = b.ticker['Sell'] + slip_point

    last_price_diff = a.ticker['Last'] - b.ticker['Last']

    a_diff = caculate_price_diff(last_price_diff,
                                 a_sell_price, a.trdfee['Sell'],
                                 b_buy_price, b.trdfee['Buy'],
                                 delta)
    b_diff = caculate_price_diff(last_price_diff,
                                 b_sell_price, b.trdfee['Sell'],
                                 a_buy_price, a.trdfee['Buy'],
                                 -delta)

    if a_diff > 0:
        # a卖b买
        result['sell_myex'] = a
        result['sell_price'] = a_sell_price
        result['buy_myex'] = b
        result['buy_price'] = b_buy_price
        result['delta'] = delta
        result['diff'] = a_diff
        result['direction'] = 'asbb'
    elif b_diff > 0:
        # a买b卖
        result['sell_myex'] = b
        result['sell_price'] = b_sell_price
        result['buy_myex'] = a
        result['buy_price'] = a_buy_price
        result['delta'] = delta     # FIXME: 这里应该 -delta ?
        result['diff'] = b_diff
        result['direction'] = 'abbs'
    else:
        result = None

    return result

def need_update_ticker(myex_comp_list):
    # {myex.name: True/False, ...}
    result = {}

    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')

    for (myex_a, myex_b) in myex_comp_list:
        result[myex_a.name] = False
        result[myex_b.name] = False

        ret = caculate_arbitrage(myex_a, myex_b)
        if not ret:
            continue

        if ret['direction'] == 'asbb':
            if myex_a.account['Stocks'] > min_trade_amount and \
               myex_b.account['Balance'] / ret['buy_price'] > min_trade_amount:
                result[myex_a.name] = True
                result[myex_b.name] = True
        elif ret['direction'] == 'abbs':
            if myex_b.account['Stocks'] > min_trade_amount and \
               myex_a.account['Balance'] / ret['buy_price'] > min_trade_amount:
                result[myex_a.name] = True
                result[myex_b.name] = True

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
            loop_count % 50 == (50 - idx)): # 让交易所在不通的循环更新
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
                myex.account_timestamp = loop_count

    for myex in myex_list: # Ticker
        t0 = time.time()
        ret = myex.get_ticker()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.ticker_timestamp = loop_count

    if is_emutest_mode():
        ticker_update_dict = {}
        for myex in myex_list:
            ticker_update_dict[myex.name] = True
    else:
        ticker_update_dict = need_update_ticker(myex_comp_list)
    for myex in myex_list: # Detph
        # 不需要每次轮询都获取深度信息
        if not ticker_update_dict[myex.name]:
            continue
        t0 = time.time()
        ret = myex.get_depth()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.depth_timestamp = loop_count

def generate_compare_list(myex_list):
    li = []
    ll = len(myex_list) - 1
    for i in range(ll):
        for j in range(ll - i):
            li.append((myex_list[i], myex_list[i+j+1]))
    return li

def float_round_down(f, prec):
    assert isinstance(prec, int)
    assert prec > 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_DOWN))

def trend_machine(myex_list, all_curr_fund, all_init_fund):
    '''
    这为趋势调仓（平仓）函数，会根据策略参数执行调仓（平仓）操作
    用到的策略参数有：
        - g_real_abtr_diff (套利差)
        - G_PARAM_MIN_TRADE_AMOUNT (最小交易量)
        - G_PARAM_TREND_MACHINE_THRESHOLD (趋势机阈值)
        - G_PARAM_TRANSFER_POSITION_MODE (调仓方式)
        - G_PARAM_TREND_FUND_PERCENT

    最重要的依据为 last_buy_price/last_sell_price （历史平均价格）
    若当前的买入和卖出和历史平均价格比较适合的话，即会执行交易操作
    每次交易只会执行实际需要交易量的 0.6，并不会一步到位买入卖出
    '''
    trend_machine_threshold = get_param('G_PARAM_TREND_MACHINE_THRESHOLD')
    base = myex_list[0].base
    quote = myex_list[0].quote

    # NOTE 调仓方式，暂时判定标准有下列几种（前两种为同行的策略）
    #   - 按照轮询次数
    #   - 套利 N 次后
    #   - 距离上一次套利轮询了 N 次后（或时间）
    # 距离上一次套利交易后多久没有套利交易，才会尝试调仓来获取更多套利机会？
    need_transfer_positions = False
    tpmode = get_param('G_PARAM_TRANSFER_POSITION_MODE')
    if tpmode == 0:     # 按照轮询次数调仓
        # 第一次进入循环 get_loop_count() 就返回 1
        if get_loop_count() % (trend_machine_threshold * 30) == 0:
            # 每 30 次学习周期后调仓 1 次
            need_transfer_positions = True
    elif tpmode == 1:   # 按照搬砖量（下单量）调仓
        # 按照策略，套利交易量达到阈值(/30)后，调一次仓（同行的策略）
        if (get_stats('STATS_ARBITRAGE_AMOUNT') * 30) > trend_machine_threshold:
            need_transfer_positions = True
    elif tpmode == 2:   # 上一次套利后到现在过了多长时间了？
        if get_loop_count() >= get_last_arbitrage_timestamp() + trend_machine_threshold * 30:
            # 自上一次套利到现在过了 30 次学习周期，调一次仓
            need_transfer_positions = True
    else:
        Log('无法使用趋势机，平仓方式参数错误：%d' % tpmode)
    if not need_transfer_positions:
        return

    LogDebug('趋势机启动，可能执行调仓操作。')

    all_FrozenBalance = 0
    all_FrozenStocks = 0
    buy_info = {}
    sell_info = {}
    # 小数点后8位
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')

    # 按照当前ticker信息构造需要的买卖信息
    for myex in myex_list:
        all_FrozenBalance += myex.account['FrozenBalance']
        all_FrozenStocks += myex.account['FrozenStocks']

        bd = {}
        # 以卖1价买
        bd['price'] = myex.ticker['Sell']
        bd['amount'] = myex.account['Balance'] / myex.ticker['Sell']
        bd['myex'] = myex
        bd['comp_price'] = myex.last_buy_price
        buy_info[myex.name] = bd

        sd = {}
        # 以买1价卖
        sd['price'] = myex.ticker['Buy']
        sd['amount'] = myex.account['Stocks']
        sd['myex'] = myex
        sd['comp_price'] = myex.last_sell_price
        sell_info[myex.name] = sd

    # NOTE: 我们的策略不应该依赖初始状态来调仓，除非有实测数据支撑
    if True:
        # 直接按照总资金的一半换商品币
        amount = all_curr_fund['total'] / all_curr_fund['price']
        amount /= 2.0
        amount = amount
    else:
        # 严格按照初始状态的商品币的数量计算
        amount = all_init_fund['stocks']

    # TODO FIXME
    target_buy_info = buy_info[myex_list[-1].name]
    target_sell_info = sell_info[myex_list[-1].name]

    # 预留给趋势机的资金比例，百分率
    # 平仓时，如果需要买入，则会多买入这个比例的商品币
    # 平仓时，如果需要卖出，则会多卖出这个比例的商品币
    trend_fund_percent = get_param('G_PARAM_TREND_FUND_PERCENT')
    trend_fund_ratio = trend_fund_percent / 100.0

    # 套利差
    abtr_diff_ratio = g_real_abtr_diff / 100.0
    # 这里的使用可以再乘以一个系数
    abtr_diff_ratio *= float(get_param('G_PARAM_TREND_ARBITRAGE_DIFFERENCE_FACTOR'))

    if all_FrozenStocks < all_curr_fund['stocks'] * 0.1 and \
       all_curr_fund['stocks'] < amount * (1.0 + trend_fund_ratio):
    ### 冻结的商品币占比不到 10% 并且，当前总商品币不够平仓需要的量，可能需要买入

        if target_buy_info['price'] < target_buy_info['comp_price'] * (1.0 - abtr_diff_ratio):
        # 当前买入价低于平均买入价的一定比率（减去套利差），即可执行交易
            myex = target_buy_info['myex']
            # 只交易差值的部分
            target_amount = abs(amount * (1.0 + trend_fund_ratio) - all_curr_fund['stocks']) * 0.6
            target_amount = min(target_amount, target_buy_info['amount'])
            # 交易前需要根据精度截断数值
            target_amount = float_round_down(target_amount, myex.amount_prec)
            target_price = float_round_down(target_buy_info['price'], myex.price_prec)
            if target_amount >= get_param('G_PARAM_MIN_TRADE_AMOUNT'):
                # 确定买入
                ret = myex.buy(target_price, target_amount)
                if not ret:
                    Log('趋势机下单失败：以 %.*f 价格买入 %.*f %s'
                        % (myex.price_prec, target_price,
                           myex.amount_prec, target_amount, myex.base))
                else:
                    myex.trend_buy_orders[ret] = {
                        'price': target_price,
                        'amount': target_amount,
                    }
                    touch_last_order_timestamp()
                    # 刷新 last_buy_price
                    refresh_myex_last_buy_price(myex_list, target_price)
                    # 更新统计信息
                    myex.stats_trend_buy_amount += target_amount
                    myex.stats_total_buy_amount += target_amount
                    Log('[%s] 执行趋势机策略，该次以价格 %.*f 买入了 %.*f 个 %s，其中理论量为：%.*f。'
                        % (myex.name,
                           prec, target_price,
                           prec, target_amount,
                           base,
                           prec, amount))

    elif all_FrozenBalance < all_curr_fund['balance'] * 0.1 and \
         all_curr_fund['stocks'] > amount * (1.0 - trend_fund_ratio):
    ### 冻结的定价币占比不到 10% 并且，当前总商品币大于平仓需要的量，可能需要卖出

        if target_sell_info['price'] > target_sell_info['comp_price'] * (1.0 - abtr_diff_ratio):
        # 当前卖出价高于平均卖出价（考虑套利差后），可以执行交易
            myex = target_sell_info['myex']
            target_amount = abs(all_curr_fund['stocks'] - amount * (1.0 - trend_fund_ratio)) * 0.6
            target_amount = min(target_amount, target_sell_info['amount'])
            target_amount = float_round_down(target_amount, myex.amount_prec)
            target_price = float_round_down(target_sell_info['price'], myex.price_prec)
            if target_amount >= get_param('G_PARAM_MIN_TRADE_AMOUNT'):
                # 确定卖出
                ret = myex.sell(target_price, target_amount)
                if not ret:
                    Log('趋势机下单失败：以 %.*f 价格卖出 %.*f %s'
                        % (myex.price_prec, target_price,
                           myex.amount_prec, target_amount, myex.base))
                else:
                    myex.trend_sell_orders[ret] = {
                        'price': target_price,
                        'amount': target_amount,
                    }
                    touch_last_order_timestamp()
                    # 刷新 last_sell_price
                    refresh_myex_last_sell_price(myex_list, target_price)
                    # 更新统计信息
                    myex.stats_trend_sell_amount += target_amount
                    myex.stats_total_sell_amount += target_amount
                    Log('[%s] 执行趋势机策略，该次以价格 %.*f 卖出了 %.*f 个 %s，其中理论量为：%.*f。'
                        % (myex.name,
                           prec, target_price,
                           prec, target_amount,
                           base,
                           prec, amount))

def make_trade_list(myex_comp_list):
    '''
    计算应该执行的交易单子
    '''
    all_trade_list = []
    slip_point = get_param('G_PARAM_SLIP_POINT')
    for (myex_a, myex_b) in myex_comp_list:
        if myex_a.delay < 2000 and myex_b.delay < 2000:
            try:
                trade = myex_a.make_trade_comp_exchange(myex_b, slip_point=slip_point)
                if trade:
                    all_trade_list.append(trade)
            except:
                Log('WTF on ARBITRAGE!')
                Log(traceback.format_exc())

    return all_trade_list

def process_arbitrage_trade(trade, max_trade_amount):
    '''
    trade结构是一个套利交易对，如 a卖b买

    return 买单id，卖单id，交易数量
    '''
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')
    buy_myex = trade['buy_myex']
    sell_myex = trade['sell_myex']
    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')

    result_buy_amount = 0.0
    result_sell_amount = 0.0

    trade_amount = trade['strategy_amount']
    if trade_amount > max_trade_amount:
        trade_amount = max_trade_amount

    trade_amount = float_round_down(trade_amount, buy_myex.amount_prec)
    if trade_amount < min_trade_amount:
        #LogDebug('该次交易数量 %.*f 少于策略设置的最小交易量 %.*f，放弃执行交易。'
        #         % (buy_myex.amount_prec, trade_amount,
        #            buy_myex.amount_prec, min_trade_amount))
        return None, None, 0.0

    target_buy_price = float_round_down(trade['buy_price'], buy_myex.price_prec)
    buy_order_id = buy_myex.buy(target_buy_price, trade_amount)
    if not buy_order_id:
        Log('下单失败：以 %.*f 价格买入 %.*f %s，取消此次套利交易'
            % (buy_myex.price_prec, target_buy_price,
               buy_myex.amount_prec, trade_amount, buy_myex.base))
        return None, None, 0.0
    else:
        buy_myex.arbitrage_buy_orders[buy_order_id] = {
            'price': target_buy_price,
            'amount': trade_amount
        }
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()
        result_buy_amount = trade_amount
        buy_myex.stats_arbitrage_buy_amount += trade_amount
        buy_myex.stats_total_buy_amount += trade_amount

    target_sell_price = float_round_down(trade['sell_price'], sell_myex.price_prec)
    sell_order_id = sell_myex.sell(target_sell_price, trade_amount)
    if not sell_order_id:
        Log('下单失败：以 %.*f 价格卖出 %.*f %s，但是套利买单已经下单成功...'
            % (sell_myex.price_prec, target_sell_price,
               sell_myex.amount_prec, trade_amount, sell_myex.base))
        # 下单失败也要继续
        #return buy_order_id, None, trade_amount
    else:
        sell_myex.arbitrage_sell_orders[sell_order_id] = {
            'price': target_sell_price,
            'amount': trade_amount
        }
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()
        result_sell_amount = trade_amount
        sell_myex.stats_arbitrage_sell_amount += trade_amount
        sell_myex.stats_total_sell_amount += trade_amount

    add_stats('STATS_ARBITRAGE_AMOUNT', trade_amount)
    add_stats('STATS_ARBITRAGE_COUNT', 1)

    if get_param('G_PARAM_COUNT_REAL_FEE'):
        # TODO 处理下单失败的情况
        fee = (target_sell_price * sell_myex.trdfee['Sell'] + \
               target_buy_price * buy_myex.trdfee['Buy']) * trade_amount / 100.0
        arbitrage_profit = (trade['sell_price'] - trade['buy_price']) * trade_amount
        arbitrage_profit -= fee
        add_stats('STATS_ARBITRAGE_PROFIT', arbitrage_profit)
    else:
        # 这个按照简易计算法计算
        arbitrage_profit = (trade['sell_price'] - trade['buy_price']) * trade_amount
        abtr_diff = g_real_abtr_diff
        arbitrage_profit *= (abtr_diff - sell_myex.trdfee['Sell'] - buy_myex.trdfee['Buy']) / abtr_diff
        add_stats('STATS_ARBITRAGE_PROFIT', arbitrage_profit)

    return buy_order_id, sell_order_id, trade_amount

def process_trade_list(myex_list, all_trade_list):
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

        if sell_myex.account['Stocks'] > buy_myex.account['Stocks']/20 and \
           sell_myex.account['Stocks'] > get_param('G_PARAM_MIN_TRADE_AMOUNT'):

            # 减掉之前交易冻结的资金
            balance = buy_myex.account['Balance'] - frozen_fund[buy_myex.name]['total_frozen_balance']
            stocks = sell_myex.account['Stocks'] - frozen_fund[sell_myex.name]['total_frozen_stocks']

            max_sell_amount = stocks
            # NOTE: 必须算上手续费，否则可能出现错误结果
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
                    Log('该次套利只成功下单买单，下单买单失败，等待取消订单...')
                else:
                    Log('该次套利只成功下单卖单，下单买单失败，等待取消订单...')
                continue

            total_trade_amount += trade_amount

    return total_trade_amount

def tune_abtr_diff(last_trade_amount):
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')
    '''
    调整套利差
    @return
        True    - 微调了套利差
        False   - 没有微调套利差

    x = get_param('G_PARAM_BASE_TRADE_AMOUNT')  # 基础交易数量
    y = last_trade_amount                       # 最近的套利交易数量
    当套利差在正常的范围的时候，调整方法为：
        - 0x  <= y <  1x    时，减套利差 0.004，要求重置 last_trade_amount
        - 1x  <= y <  20x   时，减套利差 0.001，要求重置 last_trade_amount
        - 20x <= y <= 25x   时，不调整套利差  ，要求重置 last_trade_amount
        - 25x  < y <  50x   时，不调整套利差
        - 50x  < y <= 100x  时，加套利差 0.002，要求重置 last_trade_amount
        - 100x < y <  +∞   时，加套利差 0.015，要求重置 last_trade_amount
    '''
    global g_real_abtr_diff
    base_trade_amount = get_param('G_PARAM_BASE_TRADE_AMOUNT')
    if g_real_abtr_diff < get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN'):
        g_real_abtr_diff = get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN')
    elif g_real_abtr_diff > get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MAX'):
        g_real_abtr_diff = get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MAX')
    elif last_trade_amount > base_trade_amount * 25 and \
         last_trade_amount < base_trade_amount * 50:
        pass
    else:
        if last_trade_amount < base_trade_amount:
            g_real_abtr_diff -= 0.004
        elif last_trade_amount < base_trade_amount * 20:
            g_real_abtr_diff -= 0.001
        elif last_trade_amount > base_trade_amount * 100:
            g_real_abtr_diff += 0.015
        elif last_trade_amount > base_trade_amount * 50:
            g_real_abtr_diff += 0.002
        else:
            ## FIXME: 20x <= y < 50x 这种情况没处理? (结合25x < y < 50x)
            ## 实际为 20x <= y <= 25x 这种情况没有处理（不调整套利差）
            pass
        Log('最近的套利交易数量为: %.*f，套利差更新为: %.*f。'
            % (prec, last_trade_amount, prec, g_real_abtr_diff))
        return True

    return False

def backup_trade(myorder, amount, slip_point=0.0):
    '''
    在取消未完成订单的时候，如果发现仓位不平衡，需要提交补充交易的订单的时候
    调用此函数进行交易，此函数不会考虑买1卖1的量，仅按理想交易量提交订单

    @return
        下单的交易量(amount)
    '''
    incompl_amount = myorder['Amount'] - myorder['DealAmount']
    if incompl_amount < amount:
        trade_amount = incompl_amount
    else:
        trade_amount = amount

    myex = myorder['myex']
    ret = None
    if myorder['Type'] == ORDER_TYPE_BUY:
        price = myorder['ticker']['Sell'] + slip_point
        ret = myex.buy(price, trade_amount)
        if ret:
            myex.backup_buy_orders[ret] = {'price': price, 'amount': trade_amount}
    elif myorder['Type' == ORDER_TYPE_SELL]:
        price = myorder['ticker']['Buy'] - slip_point
        ret = myex.sell(price, trade_amount)
        if ret:
            myex.backup_sell_orders[ret] = {'price': price, 'amount': trade_amount}
    else:
        Log('内部错误：order["Type"] = %d' % myorder['Type'])

    if ret is None:
        return 0.0
    else:
        return trade_amount

def clean_order_dict(myex, incompl_orders):
    arbitrage_buy_orders = {}
    trend_buy_orders = {}
    backup_buy_orders = {}
    arbitrage_sell_orders = {}
    trend_sell_orders = {}
    backup_sell_orders = {}
    for order in incompl_orders:
        oid = order['Id']
        if order['Type'] == ORDER_TYPE_BUY:
            if myex.arbitrage_buy_orders.has_key(oid):
                arbitrage_buy_orders[oid] = myex.arbitrage_buy_orders[oid]
            if myex.trend_buy_orders.has_key(oid):
                trend_buy_orders[oid] = myex.trend_buy_orders[oid]
            if myex.backup_buy_orders.has_key(oid):
                backup_buy_orders[oid] = myex.backup_buy_orders[oid]
        else:
            if myex.arbitrage_sell_orders.has_key(oid):
                arbitrage_sell_orders[oid] = myex.arbitrage_sell_orders[oid]
            if myex.trend_sell_orders.has_key(oid):
                trend_sell_orders[oid] = myex.trend_sell_orders[oid]
            if myex.backup_sell_orders.has_key(oid):
                backup_sell_orders[oid] = myex.backup_sell_orders[oid]
    myex.arbitrage_buy_orders = arbitrage_buy_orders
    myex.trend_buy_orders = trend_buy_orders
    myex.backup_buy_orders = backup_buy_orders
    myex.arbitrage_sell_orders = arbitrage_sell_orders
    myex.trend_sell_orders = trend_sell_orders
    myex.backup_sell_orders = backup_sell_orders

def process_incompl_orders(myex_list, all_curr_fund, all_init_fund):
    '''
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1

    ORDER_STATE_PENDING = 0
    ORDER_STATE_CLOSED = 1
    ORDER_STATE_CANCELED = 2

    @return
        未完成订单的总数
    '''
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')
    all_incompl_buy_amount = 0.0
    all_incompl_sell_amount = 0.0
    all_incompl_abtr_buy_amount = 0.0
    all_incompl_abtr_sell_amount = 0.0
    incompl_buy_orders = []
    incompl_sell_orders = []

    #price_prec = get_param('G_PARAM_PRICE_PREC')
    #amount_prec = get_param('G_PARAM_AMOUNT_PREC')

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

        ticker = myex.ticker
        for order in incompl_orders:
            cancel_result = False
            try:
                # FIXME: 有些交易所的参数输入必须为字符串，有些则为数字
                # 返回操作结果，true表示取消订单请求发送成功，false取消订单请求
                # 发送失败（只是发送请求成功，交易所是否取消订单最好调用exchange.GetOrders()查看）
                cancel_result = myex.cancel_order(order['Id'])
            except:
                LogDebug(traceback.format_exc())
                Log('[%s] 未能取消未完成的订单：%s' % (myex.name, str(order['Id'])))
                Log('[%s] 请检查是否给予 API 取消交易订单的权限。' % myex.name)

            if not cancel_result:
                Log('[%s] 取消订单请求发送失败，请刷新确认是否成功取消订单：%s'
                    % myex.name, str(order['Id']))
                continue
            touch_last_cancel_order_timestamp()

            incompl_amount = order['Amount'] - order['DealAmount']
            price = order['Price']
            myorder = copy.copy(order)
            oid = myorder['Id']
            if g_use_python3 and isinstance(oid, bytes):
                oid = str(oid)
            # 增加几个键
            myorder['myex'] = myex
            myorder['ticker'] = ticker
            if order['Type'] == ORDER_TYPE_BUY:
                if myex.arbitrage_buy_orders.has_key(oid):
                    myorder['order_type2'] = 'arbitrage'
                    all_incompl_abtr_buy_amount += incompl_amount
                elif myex.trend_buy_orders.has_key(oid):
                    myorder['order_type2'] = 'trend'
                elif myex.backup_buy_orders.has_key(oid):
                    myorder['order_type2'] = 'backup'
                else:
                    myorder['order_type2'] = 'unknown'
                all_incompl_buy_amount += incompl_amount
                incompl_buy_orders.append(myorder)
                # TODO
                myex.account['Balance'] += myex.account['FrozenBalance']
                myex.account['FrozenBalance'] = 0
            elif order['Type'] == ORDER_TYPE_SELL:
                if myex.arbitrage_sell_orders.has_key(oid):
                    myorder['order_type2'] = 'arbitrage'
                    all_incompl_abtr_sell_amount = incompl_amount
                elif myex.trend_sell_orders.has_key(oid):
                    myorder['order_type2'] = 'trend'
                elif myex.backup_sell_orders.has_key(oid):
                    myorder['order_type2'] = 'backup'
                else:
                    myorder['order_type2'] = 'unknown'
                all_incompl_sell_amount += incompl_amount
                incompl_sell_orders.append(myorder)
                # TODO
                pass
            else:
                Log('WTF!', order)

    if not incompl_order_count:
        return 0

    if True: # TODO
        # 直接按照总资金的一半换商品币
        default_amount = all_curr_fund['total'] / all_curr_fund['price']
        default_amount /= 2.0
    else:
        # NOTE: 我们的策略不应该依赖初始状态来调仓，除非有实测数据支撑
        # 严格按照初始状态的商品币的数量计算
        default_amount = all_init_fund['stocks']

    #if all_incompl_buy_amount > all_incompl_sell_amount:
    if all_incompl_abtr_buy_amount > all_incompl_abtr_sell_amount:
        # 这个差值是还需要买的量
        diff = all_incompl_abtr_buy_amount - all_incompl_abtr_sell_amount
        Log('正在处理未完成的买单，购买量为: %.*f' % (prec, diff))
        if all_curr_fund['stocks'] - diff * 0.6 > default_amount * 0.98:
            # 当前仓位商品币比平仓商品币多 0.6*diff ，直接撤掉订单即可
            Log('当前商品币库存较多，撤掉买单即可，无需补充买入，库存阈值为：%.*f'
                % (prec, default_amount*0.98 + diff*0.6))
        else:
            diff_tmp = diff
            for myorder in incompl_buy_orders:
                if diff_tmp < get_param('G_PARAM_MIN_TRADE_AMOUNT'):
                    break
                # 非套利订单，无需补充交易，直接取消
                # 因为趋势机会继续尝试平衡
                if myorder['order_type2'] != 'arbitrage':
                    Log('[%s] 订单 %s 为非套利买单，直接取消即可。'
                        % (myorder['myex'].name, myorder['Id']))
                    continue
                # 补充买入一次，使用卖1的价格
                diff_tmp -= backup_trade(myorder, diff_tmp,
                                         get_param('G_PARAM_SLIP_POINT'))
            if diff_tmp != diff:
                touch_last_order_timestamp()

        # TODO: 更新统计信息，如搬砖收益

    #elif all_incompl_buy_amount < all_incompl_sell_amount:
    elif all_incompl_buy_amount < all_incompl_sell_amount:
        diff = all_incompl_abtr_sell_amount - all_incompl_abtr_buy_amount
        if all_curr_fund['stocks'] + diff * 0.6 < default_amount * 1.02:
            # 当前仓位商品币比平仓商品币少 0.6*diff ，直接撤掉订单即可
            Log('当前商品币库存不多，撤销卖单即可，无需补充卖出，库存阈值为：%.*f'
                % (prec, default_amount*1.02 - diff*0.6))
        else:
            diff_tmp = diff
            for myorder in incompl_sell_orders:
                if diff_tmp < get_param('G_PARAM_MIN_TRADE_AMOUNT'):
                    break
                # 非套利订单，无需补充交易，直接取消
                # 因为趋势机会继续尝试平衡
                if myorder['order_type2'] != 'arbitrage':
                    Log('[%s] 订单 %s 为非套利卖单，直接取消即可。'
                        % (myorder['myex'].name, myorder['Id']))
                    continue
                # 补充卖出一次，使用买1的价格
                diff_tmp -= backup_trade(myorder, diff_tmp,
                                         get_param('G_PARAM_SLIP_POINT'))
            if diff_tmp != diff:
                touch_last_order_timestamp()

        # TODO: 更新统计信息，如搬砖收益

    else:
        Log('未完成的买单交易数量为：%.*f，卖单交易数量为：%.*f，数量相等，此次套利可直接取消。'
            % (prec, all_incompl_buy_amount, prec, all_incompl_sell_amount))
        # TODO: 更新统计信息，如搬砖收益

    return incompl_order_count

def _draw_table(*tables):
    global g_run_on_botvs
    if not tables:
        return

    if g_run_on_botvs:
        LogStatus('`' + '`\n`'.join(map(json.dumps, tables)) + '`')
        return

    import texttable
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')
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
        align = ['c'] * len(table['cols'])
        tab.set_cols_align(align)
        tab.set_cols_dtype(['t'] * len(table['cols']))
        tab.add_rows(table['rows'], header=False)
        Log(tab.draw())
    Log('@' * 80)

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
    if not myex_list:
        return

    # 显示的信息可以按照设置的精度显示，所以不保证显示的信息很准确
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')
    price_prec = get_param('G_PARAM_PRICE_PREC')
    amount_prec = get_param('G_PARAM_AMOUNT_PREC')

    base = myex_list[0].base
    quote = myex_list[0].quote

    # 概要信息
    table_summary = {
        'type': 'table',
        'title': '综合信息',
        'cols': [
            '状态',
            '交易对',
            '时间',
            #'交易所数量',
            '延时(ms)',

            '可用%s' % base,
            #'冻结%s' % base,
            '可用%s' % quote,
            #'冻结%s' % quote,
            '均价(%s)' % quote,
            '均价变化(%)',

            # 市值用最后成交价计算
            '市值(%s)' % quote,

            #'套利收益(%s)' % quote,
            #'套利收益率(%)',
            '收益(%s)' % quote,
            '收益率(%)'
        ],
        'rows': [],
    }

    #table_summary['cols'] = ['x'] * len(table_summary['cols'])

    # 初始信息
    row1 = [
        '初始',
        '%s/%s' % (base, quote),
        g_startup_time.replace(' ', '\n'),
        #len(myex_list),
        'N/A',

        '%.*f' % (amount_prec, all_init_fund['Stocks']),
        #'%.*f' % (amount_prec, all_init_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_init_fund['Balance']),
        #'%.*f' % (price_prec, all_init_fund['FrozenBalance']),
        '%.*f' % (price_prec, all_init_fund['price']),
        '%.*f' % (4, 0.0),

        '%.*f' % (price_prec, all_init_fund['total']),

        #'N/A',
        #'N/A',
        'N/A',
        'N/A',
    ]

    total_profit = all_curr_fund['total'] - all_init_fund['total']
    row2 = [
        '现在',
        '%s/%s' % (base, quote),
        get_strtime().replace(' ', '\n'),
        #len(myex_list),
        '%.1f' % op_delay_ms,

        '%.*f' % (amount_prec, all_curr_fund['Stocks']),
        #'%.*f' % (amount_prec, all_curr_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_curr_fund['Balance']),
        #'%.*f' % (price_prec, all_curr_fund['FrozenBalance']),
        '%.*f' % (price_prec, all_curr_fund['price']),
        '%.*f' % (4, all_curr_fund['price']/all_init_fund['price']*100.0-100.0),

        '%.*f' % (price_prec, all_curr_fund['total']),

        #get_stats('STATS_ARBITRAGE_PROFIT'),
        #get_stats('STATS_ARBITRAGE_PROFIT') / all_curr_fund['total'],
        '%.*f' % (price_prec, total_profit),
        '%.*f' % (4, total_profit / all_init_fund['total'] * 100),
    ]

    assert len(table_summary['cols']) == len(row1)
    assert len(table_summary['cols']) == len(row2)
    table_summary['rows'].append(row1)
    table_summary['rows'].append(row2)

    table0 = {
        'type': 'table',
        'title': '交易所信息',
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
            #'冻结%s' % base,
            '可用%s' % quote,
            #'冻结%s' % quote,

            '可购量',
            '手续费(%)',
            '套利交易量(%s)' % base,
            '平仓交易量(%s)' % base,
        ],
        'rows': [],
    }

    #table0['cols'] = ['x'] * len(table0['cols'])

    for myex in myex_list:
        row = [
            myex.name,
            myex.api_mode,
            '%.1f' % myex.delay,

            '%.*f' % (price_prec, myex.ticker['Buy']),
            '%.*f' % (price_prec, myex.ticker['Sell']),
            '%.*f' % (price_prec, myex.ticker['Last']),

            '%.*f' % (amount_prec, myex.account['Stocks']),
            #'%.*f' % (amount_prec, myex.account['FrozenStocks']),
            '%.*f' % (price_prec, myex.account['Balance']),
            #'%.*f' % (price_prec, myex.account['FrozenBalance']),

            # NOTE: 可购量用 卖1 价格计算
            '%.*f' % (myex.amount_prec, myex.account['Balance'] / myex.ticker['Sell']),
            '买 %.2f, 卖 %.2f' % (myex.trdfee['Buy'], myex.trdfee['Sell']),
            '%.*f' % (myex.amount_prec, myex.stats_arbitrage_buy_amount + myex.stats_arbitrage_sell_amount),
            '%.*f' % (myex.amount_prec, myex.stats_trend_buy_amount + myex.stats_trend_sell_amount),
        ]
        assert len(table0['cols']) == len(row)
        table0['rows'].append(row)

    _draw_table(table_summary, table0)

# ============================================================
### 主要流程
#       - 处理未完成订单
#       - 趋势机平仓
#       - 计算套利可能并执行套利交易
#
#
# 只有三种交易
#       - 套利交易
#       - 平仓交易
#       - 取消未完成订单后，补充未完成部分的买卖交易
#
#
# 流程优化，这样的流程可以保证账号信息不冲突，还有保证均衡的刷新间隔
#       - 刷新数据
#       - 如到了清理未完成订单的时机，并且有未完成的订单，清理并跳过本回合其他可能交易（套利，平仓）
#       - 趋势平仓，如果本轮触发了平仓交易，跳过套利交易
#       - 套利交易
def mainloop(all_init_fund, myex_list):
    global g_loop_count
    # 循环间隔，单位毫秒
    loop_interval = get_param('G_PARAM_LOOP_INTERVAL')
    # 增强学习次数
    boost_learn_count = get_param('G_PARAM_BOOST_LEARN_COUNT')
    # 趋势机阈值
    trend_machine_threshold = get_param('G_PARAM_TREND_MACHINE_THRESHOLD')
    # 最大统一精度
    prec = get_param('G_PARAM_MAX_UNIFY_PREC')

    myex_comp_list = generate_compare_list(myex_list)
    for i in myex_comp_list:
        # 初始化 delta
        i[0].init_delta(i[1])
        LogDebug('初始 delta (%s - %s)：%.*f' % (i[0].name, i[1].name,
                                                 prec, i[0].delta_dict[i[1].name]))

    # 最近的套利交易数量，套利差更新后会重置
    last_trade_amount = 0.0
    # 这个用来更新套利差的，每次循环加 1，套利差更新后重置
    tune_abtr_diff_threshold = 0

    all_curr_fund = copy.deepcopy(all_init_fund)

    # 这样可以保证第一次进入循环不睡眠
    prev_loop_time = 0.0
    while True:
        g_loop_count += 1
        loop_count = g_loop_count
        tune_abtr_diff_threshold += 1

        # 本轮清理未完成订单的数量
        this_incompl_order_count = 0
        # 本轮是否在清理未完成订单的时候执行了重试交易
        this_execute_backup_order = False
        # 本轮是否执行过趋势平仓
        this_execute_trend_order = False

        # @ 保持每次循环持续时间为 loop_interval，如果循环时间过长，不睡眠
        curr_loop_time = time.time()
        loop_time_diff_ms = (curr_loop_time - prev_loop_time) * 1000.0
        if loop_time_diff_ms < loop_interval:
            if not is_emutest_mode():
                Sleep(loop_interval - loop_time_diff_ms)

        prev_loop_time = time.time()
        this_turn_start = time.time()
        # @ 优化 account 获取，如果没有订单操作，立即切换为随机刷新
        for myex in myex_list:
            # TODO: 处理交易所出错的情况，需要冻结交易所一段时间

            if loop_count % 50 == 1 and myex.account_refresh_state == 'refresh_complete':
                # 每50次循环需要随机刷新
                # 第一次进入此分支的时候，就设置为随机刷新模式
                # 第一次进入此分支时，myex对象的构造函数已经确保更新 account 了
                # 随机刷新模式条件为：
                # 上一次更新完 account 数据后，没有进行过以下的操作
                #   - 进行买/卖操作
                #   - 取消订单操作
                # 理论上还包括以下两种，但是一般人不会在跑策略时这么做...
                #   - 充值
                #   - 提现
                myex.account_refresh_state = 'refresh_random'

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
        # @ 刷新交易所数据
        clean_exchange_data(myex_list, loop_count)  # 暂时只清理深度和延时数据
        # 获取 account, ticker, depth
        fetch_exchange_data(myex_list, myex_comp_list, loop_count)

        # @ 更新 delta
        for (myex_a, myex_b) in myex_comp_list:
            prev_delta = myex_a.delta_dict[myex_b.name]
            myex_a.tune_delta(myex_b)
            curr_delta = myex_a.delta_dict[myex_b.name]

        # @ 更新套利差
        # 阈值是魔数...
        if tune_abtr_diff_threshold > 288 * len(myex_list):
            if tune_abtr_diff(last_trade_amount):
                tune_abtr_diff_threshold = 0
                last_trade_amount = 0.0

        # @ 如果时机合适，清理未完成的订单
        #if loop_count % 99 == 1:   # 定时清理
        # NOTE: 暂时定为给它 10 个轮询时间完成订单交易
        if get_loop_count() >= get_last_order_timestamp() + get_param('G_PARAM_WAIT_FOR_ORDER'):
            this_incompl_order_count = process_incompl_orders(myex_list,
                                                              all_curr_fund,
                                                              all_init_fund)
        if this_incompl_order_count and get_loop_count() == get_last_order_timestamp():
            this_execute_backup_order = True

        # 仅有取消订单操作，但是没有执行交易的话，可以套利但不需要趋势调仓
        # 尝试过取消订单操作了，暂时跳过其他交易

        # @ 开始趋势调仓，只有达到学习阈值和本轮没有执行取消订单操作时
        if loop_count > trend_machine_threshold + boost_learn_count \
           and not this_incompl_order_count:
            # 趋势调仓
            trend_machine(myex_list, all_curr_fund, all_init_fund)
            if loop_count == get_last_order_timestamp():
                this_execute_trend_order = True

        # @ 学习完成后，开始执行可能的套利交易
        if loop_count < boost_learn_count:
            if loop_count % 100 == 1:
                Log('当前第%d次观察大盘，再观察%d次后开始交易。'
                    % (loop_count, boost_learn_count - loop_count))
        elif loop_count == boost_learn_count:
            Log('已经观察大盘到指定次数，如果监测到有利差，'
                + '将开始套利。当前轮询次数为：%d' % loop_count)
        else: # (> boost_learn_count) *** 执行策略 ***
            if loop_count % 1000 == 0:
                Log('正在观察大盘，如果监测到有利差，'
                    + '将开始套利。当前轮询次数为：%d' % loop_count)
            all_trade_list = []
            if is_emutest_mode() and \
               loop_count <= (get_last_arbitrage_timestamp() + 1 \
                        + get_param('G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE')):
                # 在观察和模拟模式，得到套利机会后要等待若干回合，
                # 否则可能反复打印同样的套利交易
                pass
            elif not this_execute_backup_order and not this_execute_trend_order:
            # 只有在本轮没有执行过重试交易和趋势平仓交易时，才尝试套利
                # 计算可能的套利交易
                all_trade_list = make_trade_list(myex_comp_list)
            # 处理这些可能套利的订单
            ret = process_trade_list(myex_list, all_trade_list)
            last_trade_amount += ret
            if ret:
                lst = []
                for ii in all_trade_list:
                    jj = copy.copy(ii)
                    jj['buy_myex'] = jj['buy_myex'].name
                    jj['sell_myex'] = jj['sell_myex'].name
                    lst.append(jj)
                print(get_loop_count())
                LogDebug('策略计算所得套利订单为：%s' % json.dumps(lst))

        this_turn_stop = time.time()
        op_delay_ms = (this_turn_stop - this_turn_start) * 1000.0
        # @ 刷新状态信息
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

def refresh_myex_last_buy_price(myex_list, last_buy_price=None):
    '''这是上一次平仓使用的价格'''
    for myex in myex_list:
        if last_buy_price is None:
            myex.last_buy_price = myex.ticker['Buy']
        else:
            myex.last_buy_price = last_buy_price

def refresh_myex_last_sell_price(myex_list, last_sell_price=None):
    '''这是上一次平仓使用的价格'''
    for myex in myex_list:
        if last_sell_price is None:
            myex.last_sell_price = myex.ticker['Sell']
        else:
            myex.last_sell_price = last_sell_price

def main(argv=None):
    global exchanges
    global g_startup_time
    g_startup_time = get_strtime()
    Log('策略开始运行于：%s' % g_startup_time)
    if len(exchanges) < 2:
        Log('只有 1 个交易所是不能运行此策略的。')
        return -1
    elif len(exchanges) > 50:
        Log('大于 50 个交易所是不能运行此策略的。')

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
        # 平均价格
        'price': 0.0,
        'total': 0.0,

        # 原始信息
        'Balance': 0.0,
        'Stocks': 0.0,
        'FrozenBalance': 0.0,
        'FrozenStocks': 0.0,
    }

    myex_list = []
    alt_price = 0.0
    for ex in exchanges:
        if is_emutest_mode():
            ex._init_ExchangeRecords()
            ex._get_new_record()
            ex._set_account(Balance=get_param('G_PARAM_EMU_BALANCE'),
                            Stocks=get_param('G_PARAM_EMU_STOCKS'))

        myex = MyExchange(ex)
        myex_list.append(myex)

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

    avg_price = alt_price / len(myex_list)

    ## test
    #for myex in myex_list:
    #    print(myex.name, myex.botvs_exchange.account)
    #    myex.buy(0.0002, 10)
    #    print(myex.botvs_exchange.GetAccount())
    #return 

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

    all_init_fund['currency'] = myex_list[0].currency
    # 这为平均价格
    if all_init_fund['stocks'] != 0.0:
        all_init_fund['price'] = (all_init_fund['total'] -
                                  all_init_fund['balance']) / all_init_fund['stocks']
    else:
        all_init_fund['price'] = avg_price

    # 从 ticker 数据初始化最近交易价格
    refresh_myex_last_buy_price(myex_list)
    refresh_myex_last_sell_price(myex_list)

    #base, quote = currency_to_base_quote(all_init_fund['currency'])
    #msg = ('初始总商品币为：%.8f %s\n' + \
    #       '初始总定价币为：%.8f %s\n' + \
    #       '初值仓总值为：%.8f %s\n' + \
    #       '初始的交易所平均价格为：%.8f') % \
    #        (all_init_fund['stocks'], base,
    #         all_init_fund['balance'], quote,
    #         all_init_fund['total'], quote,
    #         all_init_fund['price'])
    #Log(msg)

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
