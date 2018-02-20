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
import os.path
import signal
import logging
import base64
from logging.handlers import RotatingFileHandler
from Crypto.Cipher import AES

__all__ = []

g_use_python3 = (sys.version_info[0] == 3)

g_version_info = (1, 4, 0)
g_version = '.'.join(map(str, g_version_info))
g_save_birth_time = ''

# TODO
# [X] 支持模拟交易模式
# [X] need_update_depth 考虑平仓时需要的深度信息
# [X] 处理滑点问题
# [X] 处理下单失败的情况，尤其是套利下单
# [X] 存档功能
# [X] 检查所有除法操作，保证被除数不为零
# [X] 异步优化
# [X] 处理最小交易量的问题（在制作order时判断）
# [X] 处理获取的 ticker 的信息不全的情况，例如 Sell 和 Buy 缺失
# [X] 修正多次round down之后，数字持续变小的问题
#     例如 0.0034202 一次 rd 后是 0.003420，再一次 rd 后变成 0.003419
# [X] 修正计算得到的余额跟实际的有差距导致下单失败的情况
#     [OKEX] buy(0.09960000, 0.00105113) = None, 买入失败：余额 0.00010469 < 0.00010480
# [ ] 完善策略参数检查和错误提示
# [X] 支持设置初始的总余额和总币数，方便资金转出转入
# [ ] 完善取消的订单的处理（在买卖的时候自动撮合）
# [ ] 重试平仓的终极绝招，在任意的交易所下重试平仓的单！只要保证行情是交叉的即可

# ver. 2.0
# [ ] 实现 close_retry_arbit_reverse
# [ ] 有些交易所有频率限制，需要处理这种情况 (Quoinex，300次/5分钟)
# [ ] 盈利(暂不考虑亏损)的时候，扩大币数以实现利滚利
# [ ] 重试套利交易的时候，可以以更好的价格进行，不需要一定以套利的时候的价格
# [ ] 支持交易所不同的价格和数量精度
# [ ] 最小交易支持以 stocks 或 balance 的方式计算

# ==================== 以上处理模块 ====================
'''
变量：
    - g_run_on_botvs
    - G_PARAM_EMU_MODE
    - G_PARAM_BAKTEST_MODE

模式：
    - botvs 实盘
        * g_run_on_botvs = True
        * G_PARAM_EMU_MODE = False
        * G_PARAM_BAKTEST_MODE (N/A)
    - botvs 模拟
        * g_run_on_botvs = True
        * G_PARAM_EMU_MODE = True
        * G_PARAM_BAKTEST_MODE (N/A)
    - 本地 botvs 实盘
        * g_run_on_botvs = False
        * G_PARAM_EMU_MODE = False
        * G_PARAM_BAKTEST_MODE = False
    - 本地 botvs 模拟
        * g_run_on_botvs = False
        * G_PARAM_EMU_MODE = True
        * G_PARAM_BAKTEST_MODE = False
    - 本地数据回测
        * g_run_on_botvs = False
        * G_PARAM_EMU_MODE = (N/A)
        * G_PARAM_BAKTEST_MODE = True
'''

g_startup_time = ''
g_run_on_botvs = True
g_running = True

# 这个可以作为时间戳，策略的时间戳精度即为轮询间隔
g_loop_count = 0
# 此次套利的所有的交易所
g_myex_list = []
g_all_init_fund = {}
# 实际的套利差，因为这个要经常更新
g_real_arbit_diff = 0.001

# 最后一次下单的时间戳，无论什么方式的下单都更新，如 套利，平仓
g_last_order_timestamp = 0
# 最后一次取消订单的时间戳
g_last_cancel_order_timestamp = 0
# 最后一次进行套利交易的时间戳
g_last_arbitrage_timestamp = 0

# 统计信息，理论上这些统计信息都是只能加不能减的
# FIXME: 这个可以不需要了
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
    'G_PARAM_DEBUG_MODE': False,

    # 不考虑现价差价趋势进行套利, 即如果为 True, delta 将恒为 0
    # NOTE: 可能对 beta rock 有影响
    'G_PARAM_IGNORE_LAST_DIFF': True,

    # 学习速度，值越大学习越快，可取值范围 1-4
    # 具体为调整 delta 的速率
    # 对于变动慢的，就选低档，对于变动块的，比如无手续费小波段套利，就选高档
    'G_PARAM_LEARN_SPEED': 2,

    # 首次调整价格差价时的调整参数，百分率
    # 即首次计算价格差时，对这个价格差的接受程度
    # 建议 10，波动大的币种可以设定大一些。这个值越大，
    # 初始学习周期理论上来说需时就越小。只发挥一次作用。
    'G_PARAM_DELTA_PARAM': 65,

    # 仅以 stocks 来计算仓位偏移，否则会根据现价、stocks、balance来计算偏移
    # NOTE: 现版本我们仅支持以 stocks 方式来计算
    'G_PARAM_POSITION_OFFSET_FOR_STOCKS': True,

    # 模拟测试模式，即用历史数据测试，无需实时获取信息来测试
    # 在botvs平台无法使用此模式
    'G_PARAM_BAKTEST_MODE': True,

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

    # 内部密语
    'G_PARAM_MAGIC': '',

    # ==================== 以上参数不导出，仅内部使用 ====================

    # 轮询间隔，毫秒
    'G_PARAM_LOOP_INTERVAL': 1000,

    # 交易所的轮询周期倍率
    # 逗号分隔的整数，如 "1, 2" 表示第 2 个交易所轮询周期为常规轮询周期 2 倍
    'G_PARAM_EXCHANGE_INTERVAL_TIMES': '',

    # 是否启用异步模式
    'G_PARAM_ENABLE_ASYNC_MODE': True,

    # 是否启用增强的异步模式
    'G_PARAM_ENABLE_BOOST_ASYNC': True,

    # 是否清空所有收益日志
    'G_PARAM_RESET_PROFIT_LOG': False,

    # 是否优先使用 websocket 模式
    # 一般 websocket 提供更低的延时，但不是每个交易所都支持
    'G_PARAM_USE_WEBSOCKET': True,

    # botvs 平台上的测试模式，仅在 botvs 平台上运行时才有效
    # 即所有交易都是模拟的，不是实际连接到交易所交易
    'G_PARAM_EMU_MODE': True,
    # 模拟模式的账号余额，实盘模式会忽略此参数
    'G_PARAM_EMU_BALANCE': 0.075,
    # 模拟模式的账号余币，实盘模式会忽略此参数
    'G_PARAM_EMU_STOCKS': 20.0,
    # 模拟模式进行套利交易后，暂停检测套利的轮询次数
    # 因为模拟模式的交易不影响市场，所以如果套利后不暂停，
    # 可能会马上再进行同样的套利，虽然会受余额限制。
    # 不暂停就设置为 0
    'G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE': 10,

    # 实盘模式下，套利交易后，等待多少回合再进行下一次套利
    'G_PARAM_PAUSE_ROUND_AFTER_TRADE': 1,

    # 是否自动取消冻结的订单
    'G_PARAM_ENABLE_CANCEL_ORDERS': True,

    # 订单冻结超过此轮询次数后才会取消
    'G_PARAM_WAIT_FOR_ORDER': 10,

    # 是否允许强制平仓，若不允许的话，当出现极端情况的时候，将会无法套利
    'G_PARAM_ENABLE_FORCE_CLOSE': False,

    # 总仓位偏移超过此阈值时，就会执行强制平仓
    'G_PARAM_FORCE_CLOSE_OFFSET_THRESHOLD': 50,

    # 存档名称。空字符串表示不开启存档功能
    #'G_PARAM_SAVE_FILE_NAME': 'test.sav',
    'G_PARAM_SAVE_FILE_NAME': '',

    # 是否需要从存档读取初始信息来执行策略
    # 如果为否，则不会从存档初始化策略的初始信息，并将新的存档信息覆盖之
    # 不开启存档功能的话，忽略此选项
    'G_PARAM_INIT_FROM_SAVE': True,

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

    # 每单的最少交易数量
    # 这个一般根据交易所的限制设置，如有些交易所对某些币有最小交易量限制的话
    # 如果交易所没有最小交易数量限制的话，一般设置为交易数量精度的最小单位
    # 如交易数量精度为 4，则最小交易量可设置为 0.0001
    'G_PARAM_MIN_TRADE_AMOUNT': 0.01,

    # 增强学习次数（这个轮询次数后开始套利）
    # NOTE: 我们暂时不需要这个功能
    'G_PARAM_BOOST_LEARN_COUNT': 0,

    # 滑点，根据设置的币种设置，不然会有灾难性后果！
    # 为了套利交易的快速成交，买卖时需要额外付出的价格，最小可设置为 0.0
    # 滑点只在套利计算时才考虑，其他的交易均不考虑
    # 套利差会在滑点造成的更小差价(-滑点*2)的基础上计算
    # 所以可能由于滑点的原因导致套利差变化
    # 如果滑点设置错误，将因为计算到的差价为负数而无法套利
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

    # 交易所商品币基准数量
    # 类似交易费率，逗号分隔的数量，对应于相应的交易所
    # 留空表示不设置，不设置就会使用存档的初始值或策略运行时的初始值
    'G_PARAM_EXCHANGE_BASE_STOCKS': '',

    # 交易费率(%), 按买卖顺序添加
    # 如你的交易所顺序为 okex, zb, 交易费率为 0.1, 0.1, 0.2, 0.2
    # 则表示 okex 的买手续费为 0.1%, 卖手续费为 0.1%, zb 的分别为 0.2% 和 0.2%
    'G_PARAM_TRADE_FEE': ' , , , , , , 0.1, 0.1',

    # 费率模式，逗号分隔的列表，如：0, 0, 1
    'G_PARAM_TRADE_FEES_MODES': '',

    # 用于控制哪个交易所可用于交易
    # 类似交易所费率，逗号分隔的标志，如："0, 1, 1"，表示禁用第一个交易所
    # 留空表示不启用此功能
    'G_PARAM_ENABLED_FLAGS': '1,1',

    # 是否自定义初始总资产
    'G_PARAM_CUSTOM_INIT_FUND': False,

    # 自定义的初始总余币
    'G_PARAM_CUSTOM_INIT_STOCKS': 0.0,

    # 自定义的初始总余额
    'G_PARAM_CUSTOM_INIT_BALANCE': 0.0,
}

def get_param(name, default=None):
    '''获取策略参数'''
    global ALL_PARAMETERS
    try:
        return eval(name)
    except NameError:
        return ALL_PARAMETERS.get(name, default)

def _set_param(name, value):
    global ALL_PARAMETERS
    ALL_PARAMETERS[name] = value

def get_loop_count():
    global g_loop_count
    return g_loop_count

g_logger = None
g_logfname = 'symarbit.log'
def mylog(msg, *args, **kwargs):
    try:
        if sys.stdout.isatty():
            if args:
                print(msg % args)
            else:
                print(msg)
    except:
        pass

    global g_logger
    global g_logfname
    if g_logger is None:
        logfname = g_logfname
        #logfname = os.path.splitext(os.path.basename(sys.argv[0]))[0] + '.log'
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        maxBytes = 1 * 1024 * 1024
        backupCount = 100
        g_logger = logging.getLogger(logfname)
        #g_logger.setLevel(logging.INFO)
        g_logger.setLevel(logging.DEBUG)
        handle = RotatingFileHandler(os.path.abspath(logfname),
                                     maxBytes=maxBytes,
                                     backupCount=backupCount)
        handle.setFormatter(formatter)
        g_logger.addHandler(handle)

    level = kwargs.get("level", logging.INFO)
    if level == logging.DEBUG:
        g_logger.debug(msg, *args)
    elif level == logging.INFO:
        g_logger.info(msg, *args)
    elif level == logging.WARNING:
        g_logger.warning(msg, *args)
    elif level == logging.ERROR:
        g_logger.error(msg, *args)
    elif level == logging.CRITICAL:
        g_logger.critical(msg, *args)
    else:
        g_logger.critical(msg, *args)

def init_log_func(log_func):
    bak_Log = log_func
    def _Log(*args):
        if get_param('G_PARAM_DEBUG_MODE'):
            return bak_Log('[%08d]' % get_loop_count(), *args)
        else:
            return bak_Log(*args)
    def _mylog(*args, **kwargs):
        mylog(('[%08d] ' % get_loop_count()) + ' '.join(map(str, args)),
              level=kwargs.get('level', logging.INFO))
    def Log(*args):
        _mylog(*args, level=logging.INFO)
        _Log(*args)
    def LogDebug(*args):
        _mylog(*args, level=logging.DEBUG)
        if get_param('G_PARAM_DEBUG_MODE'):
            return _Log(*args)
    def LogTrade(*args):
        '''所有交易操作的日志，如买，卖，取消'''
        _mylog(*args, level=logging.WARNING)
        return _Log(*args)
    def LogError(*args):
        _mylog(*args, level=logging.ERROR)
        return _Log(*args)

    g = globals()
    for name in ('_Log', '_mylog', 'Log', 'LogDebug', 'LogTrade', 'LogError'):
        g[name] = eval(name)

if __name__ == '__main__':
    try:
        exchanges
        init_log_func(Log)
    except NameError:
        g_run_on_botvs = False
        if get_param('G_PARAM_BAKTEST_MODE'):
            from emutest import *
            if get_param('G_PARAM_DEBUG_MODE'):
                import emutest
                emutest._get_tick = get_loop_count
        else:
            import mybotvs
            with open('exchanges.json') as fp:
                mybotvs._init(json.load(fp))
            from mybotvs import *

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

def sub_stats(key, val):
    global g_stats
    g_stats[key] -= val

def get_stats(key):
    global g_stats
    return g_stats.get(key)

def is_run_on_botvs():
    global g_run_on_botvs
    return g_run_on_botvs

def is_emulate_mode():
    '''
    botvs 平台上的测试模式
    - 返回的 account 为固定值
    - 买卖一定成功
    - 每次买卖后，下次更新account，直接从上次的买卖数据计算
    - 其他和 viewer 一样

    botvs 或 本地 botvs 的模拟模式生效时返回 True
    '''
    if is_run_on_botvs():
        return get_param('G_PARAM_EMU_MODE')
    else:
        if is_baktest_mode():
            return False
        else:
            return get_param('G_PARAM_EMU_MODE')

def is_baktest_mode():
    '''
    用数据库的历史记录模拟测试
    '''
    if is_run_on_botvs():
        return False
    return get_param('G_PARAM_BAKTEST_MODE', True)

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
    if not g_use_python3:
        if isinstance(data, unicode):   # pylint: disable=E0602
            return data.encode()
        return data

    if isinstance(data, bytes):      return data.decode()
    #if isinstance(data, (str, int)): return str(data)
    if isinstance(data, dict):       return dict(map(bytes2str, data.items()))
    if isinstance(data, tuple):      return tuple(map(bytes2str, data))
    if isinstance(data, list):       return list(map(bytes2str, data))
    if isinstance(data, set):        return set(map(bytes2str, data))

    return data

def unicode2str(data):
    '''主要用于把python2的json的unicode全部转为字符串'''
    if g_use_python3:
        return data

    if isinstance(data, dict):      return dict (map(unicode2str, data.items()))
    if isinstance(data, tuple):     return tuple(map(unicode2str, data))
    if isinstance(data, list):      return list (map(unicode2str, data))
    if isinstance(data, set):       return set  (map(unicode2str, data))
    if isinstance(data, unicode):   return data.encode()    # pylint: disable=E0602

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

def pjson(j): # pylint: disable=E0102
    Log(json.dumps(norm4json(j), indent=4, sort_keys=True))

class BotVSGo():
    def __init__(self, data):
        self.data = data

    def wait(self, timeout):
        return self.data, True

class MyExchange(object):
    _oid = 0

    # 手续费模式，现在所知的手续费模式分为 maker 和 taker
    # 我们的策略只能用 taker 的手续费
    # 现阶段，单一模式（maker或taker）的买卖手续费一般都是一样的
    # 而收取手续费的方式不一
    #   - FEES_MODE_FORWARD     <- 扣除收取到的资产(binance, huobipro, okex, ...)
    #   - FEES_MODE_BALANCE     <- 扣除余额不扣取币(cryptopia)
    #   - FEES_MODE_STOCKS      <- 扣除币不扣除余额(暂时未发现有这种类型)
    FEES_MODE_FORWARD = 0
    FEES_MODE_BALANCE = 1
    # NOTE: 这种方式很难计算，所得的为 quote，
    #       但是要额外消耗 (amount * sell_fee_ratio) 的 stocks
    #       earn = price * amount - price * (amount * sell_fee_ratio)
    #       所幸未发现有交易所使用这种方法收取手续费，okex现货证实为 FORWARD 类型
    #FEES_MODE_STOCKS  = 2   # 这个暂时不实现

    def __init__(self, botvs_exchange):
        global TRDFEE_DICT
        ### ========== 基础信息, 只读, 不变 ==========
        self.botvs_exchange = botvs_exchange
        self.born_time = time.time()

        self.currency = bytes2str(self.botvs_exchange.GetCurrency())
        self.base, self.quote = currency_to_base_quote(self.currency)

        # 这两个信息只要一次获取即可
        self.name = bytes2str(self.botvs_exchange.GetName())
        if self.name == 'Exchange':
            self.name = bytes2str(self.botvs_exchange.GetLabel())

        # 精度，一般交易所的精度都是小数点后 8 位
        self.price_prec = get_param('G_PARAM_PRICE_PREC')
        self.amount_prec = get_param('G_PARAM_AMOUNT_PREC')
        ### ----------------------------------------

        ### ========== account, ticker, depth ==========
        ### ticker 每 tick 必须刷新, account 和 depth 可按需刷新
        if is_emulate_mode():
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

        # 本交易所的基础仓位
        self.base_stocks = self.account['Stocks'] + self.account['FrozenStocks']

        # 轮询周期为 tick 的多少倍
        self.inter_times = 1

        # 后续可重新设置手续费
        self.trdfee = copy.deepcopy(TRDFEE_DICT.get(self.name.lower(), DEFAULT_TRDFEE))
        self.api_mode = 'REST' # 默认为 'REST', 有些交易所支持 'websocket'
        self.delay = 0.0

        self.enabled = True

        # 国内交易所一般使用这种模式
        self.fees_mode = self.FEES_MODE_FORWARD
        #self.fees_mode = self.FEES_MODE_BALANCE

        # 'refresh_instant'     - 立即刷新
        # 'refresh_random'      - 随机刷新
        # 'refresh_complete'    - 刷新完成
        # 因为一般交易所的api实现用，获取account信息延时都比较大，
        # 并且，如果没有发生交易，account的状态理论上是不变的
        # 所以刷新account需要优化
        #   - 只有执行交易操作后，才需要刷新account
        #   - 观察的时候，轮询N次后才刷新一次
        self.account_refresh_state = 'refresh_complete'

        # NOTE 未实现
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
        # aim:
        #   arbit -> 套利交易
        #   close -> 平仓
        #         - close_force                   强制平仓
        #         - close_retry_arbit             重试套利平仓
        #         - close_arbit_reverse           反向套利平仓
        #         - close_retry_arbit_reverse     重试反向套利平仓(暂时不实现)
        #
        # str(order_id): {
        #   'id_type': id 的原始类型，可能为 int 或 str
        #   'aim': aim,
        #   'type': buy/sell,
        #   'price': x,
        #   'amount': y,
        #   'tick': tick,
        #   'pair_info': {}, # close_retry_arbit 特有
        #   'pair_oid': oid, # arbit 特有
        #   'timestamp': time.time(), [未实现]
        # }
        # 
        self.executed_orders = {}

        ### NOTE
        ### 下面的交易量统计信息都是在本策略下单时统计的，如果发生了取消未完成的订单，
        ### 那么这些统计信息都是不准确的，暂时无法做到绝对准确
        ### 绝对准确需要访问交易所获取确切的交易量，但是这无法区分这些交易量是用来
        ### 套利还是平仓的

        # NOTE
        #   - 下单成功即统计
        #   - CancelOrder() 返回成功即统计
        #   - 根据获取到的当前信息统计, 可能跟实时情况不一致, 如取消订单状态
        # {order,cancel}.aim.type.{amount,count}
        # echo {order,cancel}.{arbit,close_retry_arbit,close_arbit_reverse,close_force,close_retry_arbit_reverse}.{buy,sell}.{amount,count}
        self.stats = {}

        # 等待强制平仓的信息
        self.pending_force = {
            'type': 'buy', # or 'sell'
            'amount': 0.0,
            #'volume': 0.0, # 这个可能为负，暂时不实现
        }

        # for botvs test mode
        self.next_account = copy.deepcopy(self.account)

    def __repr__(self):
        return "MyExchange('%s')" % self.name

    def __str__(self):
        return self.__repr__()

    @property
    def buy_fee_ratio(self):
        return self.trdfee['Buy'] / 100.0

    @property
    def sell_fee_ratio(self):
        return self.trdfee['Sell'] / 100.0

    def will_update(self):
        return (get_loop_count() - 1) % self.inter_times == 0

    def is_latest(self):
        '''
        如果不是最新的信息（或者交易所维护），以下交易均停止：
            - 套利
            - 重试套利
            - 强制平仓
        '''
        if not self.enabled:
            return False
        tick = get_loop_count()
        return self.account_tick == tick and self.ticker_tick == tick and self.depth_tick == tick

    def is_pending_force(self):
        return self.pending_force['amount'] > 0.0

    def reset_pending_force(self):
        self.pending_force['amount'] = 0.0

    def get_max_order_buy_amount(self, buy_price, Balance=None):
        '''指下单时能设置的最大买的数量，不是到手的数量'''
        if buy_price <= 0.0:
            return 0.0
        Balance = self.account['Balance'] if Balance is None else Balance
        if self.fees_mode == self.FEES_MODE_FORWARD:
            #max_buy_amount = (Balance / buy_price) * (1.0 - self.buy_fee_ratio)
            # FIXME: 未确认最小交易量是下单量为准还是到手量为准
            #        暂时假定以下单量为准
            max_buy_amount = Balance / buy_price
        else:
            max_buy_amount = (Balance / buy_price) / (1.0 + self.buy_fee_ratio)
        # 比实际量少 0.1%，避免由于浮点误差导致买入失败
        return max_buy_amount * 0.999

    def get_max_order_sell_amount(self):
        '''指下单时能设置的最大卖的数量，不是到手的数量'''
        return self.account['Stocks']

    def set_trade_fee(self, buy_fee=None, sell_fee=None):
        if not buy_fee is None:
            self.trdfee['Buy'] = float(buy_fee)
        if not sell_fee is None:
            self.trdfee['Sell'] = float(sell_fee)

    def add_raw_stats(self, k, v):
        self.stats.setdefault(k, 0.0)
        self.stats[k] += v

    def add_stats(self, order_or_cancel, aim, buy_or_sell, amount_or_count, value):
        key = '.'.join([order_or_cancel, aim, buy_or_sell, amount_or_count])
        self.stats.setdefault(key, 0.0)
        self.stats[key] += value

    def get_stats(self, order_or_cancel, aim, buy_or_sell, amount_or_count, d=0.0):
        key = '.'.join([order_or_cancel, aim, buy_or_sell, amount_or_count])
        return self.stats.get(key, d)

    def calc_cost(self, price, amount):
        '''计算买入的花费'''
        if self.fees_mode == self.FEES_MODE_FORWARD:
            cost = price * amount
        elif self.fees_mode == self.FEES_MODE_BALANCE:
            cost = price * amount * (1.0 + self.buy_fee_ratio)
        else:
            cost = price * amount
        return cost

    def calc_earn(self, price, amount):
        '''计算卖出的所得'''
        sell_fee_ratio = self.trdfee['Sell'] / 100.0
        if self.fees_mode == self.FEES_MODE_FORWARD:
            earn = price * amount * (1.0 - sell_fee_ratio)
        elif self.fees_mode == self.FEES_MODE_BALANCE:
            earn = price * amount * (1.0 - sell_fee_ratio)
        else:
            earn = price * amount * (1.0 - sell_fee_ratio)
        return earn

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

    def get_position_offset(self):
        '''仓位偏移需要算上冻结的资产'''
        #offset = caculate_position_offset(
        #    self.account['Stocks'] + self.account['FrozenStocks'],
        #    self.account['Balance'] + self.account['FrozenBalance'],
        #    self.ticker['Last'])
        stocks = self.account['Stocks'] + self.account['FrozenStocks']
        init_stocks = self.base_stocks
        if init_stocks <= 0.0:
            return 100.0
        offset = (stocks / init_stocks * 100.0 - 100.0)
        # 这个偏移只要取一定精度的结果就好了
        offset = float_round_down(offset, 2)
        if offset == 0.0:
            offset = 0.0
        else:
            offset = -offset
        return offset

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

    def Go(self, method, *args):
        # 暂时只在 botvs 实盘的时候才使用异步模式
        if is_run_on_botvs() and not is_emulate_mode():
            td = self.botvs_exchange.Go(method, *args)
            return {'myex': self, 'method': method, 'thread': td, 'time': time.time()}

        if is_run_on_botvs() and is_emulate_mode() and method in {'GetTicker', 'GetDepth'}:
            td = self.botvs_exchange.Go(method, *args)
            return {'myex': self, 'method': method, 'thread': td, 'time': time.time()}

        if method == 'GetAccount':
            if is_emulate_mode():
                td = BotVSGo(copy.deepcopy(self.next_account))
            else:
                td = BotVSGo(self.botvs_exchange.GetAccount())
        elif method == 'GetTicker':
            td = BotVSGo(self.botvs_exchange.GetTicker())
        elif method == 'GetDepth':
            td = BotVSGo(self.botvs_exchange.GetDepth())
        else:
            Log('[%s] 内部错误：Go(%s, **%s)' % (self.name, repr(method), repr(args)))
            assert False

        return {'myex': self, 'method': method, 'thread': td, 'time': time.time()}

    def _emu_buy(self, price, amount):
        buy_fee_ratio = self.trdfee['Buy'] / 100.0
        if self.fees_mode == self.FEES_MODE_FORWARD:
            cost = price * amount
            earn_stocks = amount * (1.0 - buy_fee_ratio)
        else:
            cost = price * amount * (1.0 + buy_fee_ratio)
            earn_stocks = amount
        if self.next_account['Balance'] < cost:
            LogError('[%s] 买入失败：余额 %.8f < %.8f'
                     % (self.name, self.next_account['Balance'], cost))
            return None
        self.next_account['Balance'] -= cost
        self.next_account['Stocks'] += earn_stocks
        type(self)._oid += 1
        return type(self)._oid

    def buy(self, price, amount):
        # NOTE: 返回 None 表示失败，其他表示成功
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        # FIXME: 'Zaif' 交易所据说会发生异常情况
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        # NOTE: 这里不能 round，只在执行 buy 之前 round
        #real_price = round_buy_price(price)
        #real_amount = round_amount(amount)
        real_price = price
        real_amount = amount
        if is_emulate_mode():
            oid = self._emu_buy(price, amount)
        else:
            try:
                oid = self.botvs_exchange.Buy(real_price, real_amount)
            except:
                LogDebug(traceback.format_exc())
                oid = None
        LogTrade('[%s] buy(%.*f, %.*f) = %s' % (self.name,
                                                self.price_prec, real_price,
                                                self.amount_prec, real_amount,
                                                repr(oid)))
        return bytes2str(oid)

    def _emu_sell(self, price, amount):
        if self.next_account['Stocks'] < amount:
            LogError('[%s] 卖出失败：余币 %.8f < %.8f'
                     % (self.name, self.next_account['Stocks'], amount))
            return None
        sell_fee_ratio = self.trdfee['Sell'] / 100.0
        earn = price * amount * (1.0 - sell_fee_ratio)
        self.next_account['Balance'] += earn
        self.next_account['Stocks'] -= amount
        type(self)._oid += 1
        return type(self)._oid

    def sell(self, price, amount):
        # NOTE: 返回 None 表示失败，其他表示成功
        '''
        返回订单编号，可用于查询订单信息和取消订单
        '''
        # FIXME: 'Zaif' 交易所据说会发生异常情况
        # 发生交易，必须刷新account
        self.account_refresh_state = 'refresh_instant'
        # NOTE: 这里不能 round，只在执行 sell 之前 round
        #real_price = round_sell_price(price)
        #real_amount = round_amount(amount)
        real_price = price
        real_amount = amount
        if is_emulate_mode():
            oid = self._emu_sell(price, amount)
        else:
            try:
                oid = self.botvs_exchange.Sell(real_price, real_amount)
            except:
                LogDebug(traceback.format_exc())
                oid = None
        LogTrade('[%s] sell(%.*f, %.*f) = %s' % (self.name,
                                                 self.price_prec, real_price,
                                                 self.amount_prec, real_amount,
                                                 repr(oid)))
        return bytes2str(oid)

    def get_account(self):
        if is_emulate_mode():
            self.account = copy.deepcopy(self.next_account)
            return self.account
        try:
            account = bytes2str(self.botvs_exchange.GetAccount())
        except:
            LogDebug(traceback.format_exc())
            account = None
        if account is None:
            LogError('[%s] 获取 Account 数据失败' % self.name)
            return None
        if self.account != account:
            self.account_change_tick = get_loop_count()
        self.account = account
        self.account_refresh_state = 'refresh_complete'
        return self.account

    def get_ticker(self):
        try:
            ticker = bytes2str(self.botvs_exchange.GetTicker())
        except:
            LogDebug(traceback.format_exc())
            ticker = None
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
        try:
            depth = bytes2str(self.botvs_exchange.GetDepth())
        except:
            LogDebug(traceback.format_exc())
            depth = None
        if depth is None:
            LogError('[%s] 获取 Depth 数据失败' % self.name)
            return None
        self.depth = depth
        return self.depth

    def get_orders(self):
        if is_emulate_mode():
            return []
        try:
            return bytes2str(self.botvs_exchange.GetOrders())
        except:
            LogDebug(traceback.format_exc())
            return []

    def cancel_order(self, oid, buy_or_sell=None):
        self.account_refresh_state = 'refresh_instant'
        result = False
        if is_emulate_mode():
            result = True
        try:
            result = self.botvs_exchange.CancelOrder(oid)
        except:
            LogDebug(traceback.format_exc())
            result = False
        if buy_or_sell:
            LogTrade('[%s] cancel_%s_order(%s) = %s' % (self.name, buy_or_sell,
                                                        str(oid), repr(result)))
        else:
            LogTrade('[%s] cancel_order(%s) = %s' % (self.name,
                                                     str(oid), repr(result)))
        return result

    def _make_arbit_trade(self, myex_b, slip_point=0.0):
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
            result['buy1_amount'] = abuy1_amount
            result['sell1_amount'] = bsell1_amount
            result['amount'] = min(abuy1_amount, bsell1_amount)
        elif result['direction'] == 'abbs':
            # a买b卖
            result['buy1_amount'] = bbuy1_amount
            result['sell1_amount'] = asell1_amount
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
        delta = trade['delta']

        min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
        if sell_myex.account['Stocks'] > (buy_myex.account['Stocks'] + min_trade_amount) * 8:
            # 卖单的交易所的商品币是买单的交易所的商品币的 8 倍还多
            # 此次套利的交易量可以扩大
            strategy_amount = (sell_myex.account['Stocks'] - buy_myex.account['Stocks']) * 0.6
            #LogDebug('交易数量需要扩大：%.*f -> %.*f' %
                     #(amount_prec, trade['amount'], amount_prec, strategy_amount))
        else:
            diff = trade['sell_price'] - trade['buy_price'] - delta
            try:
                trade_amount_magic = get_param('G_PARAM_TRADE_AMOUNT_MAGIC')
                param = diff / (abs(delta) + trade['buy_price'] / (trade_amount_magic*100.0))
            except ZeroDivisionError:
                Log('ZeroDivisionError: %s' % json.dumps(norm4json(trade)))
                param = 1.0
            strategy_amount = get_param('G_PARAM_BASE_TRADE_AMOUNT') * param

        max_sell_amount = sell_myex.get_max_order_sell_amount()
        max_buy_amount = buy_myex.get_max_order_buy_amount(trade['buy_price'])

        if min(max_sell_amount, max_buy_amount, trade['amount']) < min_trade_amount:
            return None

        # 根据策略算出的交易量，这是在之前算得的交易量上微调得到的，更新的结果
        trade['strategy_amount'] = strategy_amount
        # 最大的可以买的量，最大的可以卖的量，根据买卖挂单算的可以买卖的最小量
        trade['max_buy_amount'] = max_buy_amount
        trade['max_sell_amount'] = max_sell_amount
        return trade

def caculate_price_diff(sell_price, sell_fee,
                        buy_price, buy_fee,
                        arbit_diff,
                        delta_sell2buy,
                        fees_mode=MyExchange.FEES_MODE_FORWARD):
    '''
    比较两个交易所的差价
    sell_price 为卖单交易所的卖价格，一般为订单薄的买1价
    sell_fee 百分率
    buy_price 为买单交易所的买价格，一般为订单薄的卖1价
    buy_fee 百分率

    arbit_diff 套利差，百分率
    delta_sell2buy 此为 (卖单交易所 - 买单交易所) 的 delta，注意符号

    fees_mode 买方的费率模式
    '''
    buy_fee_ratio = buy_fee / 100.0
    sell_fee_ratio = sell_fee / 100.0
    # NOTE: 把套利差算到费率那里，其实是指每次套利必须至少获取此比例的利润
    fee_ratio = arbit_diff / 100.0
    # 计算套利时，可以忽略交易的手续费，这只在有特殊需要的时候才使用
    if not get_param('G_PARAM_IGNORE_TRADE_FEE'):
        # 这是原版，仅作参考
        #fee_ratio += sell_fee_ratio + buy_fee_ratio
        #price_diff = sell_price - buy_price - (buy_price * fee_ratio) - delta_sell2buy
        # ----------------------------------------
        #fee = sell_fee + buy_fee + alt_arbit_diff_percent
        #price_diff = sell_price - buy_price * (1 + fee * 1.0/ 100) - delta_sell2buy
        # ========================================
        # FEES_MODE_FORWARD 的时候, 计算方式不一样
        #   - cost = b * a / (1-bf) <- FEES_MODE_FORWARD
        #   - cost = b * a * (1+bf) <- FEES_MODE_BALANCE
        # TODO: 套利差应该以新的买卖差价除以新买价计算（计算手续费的话）
        if fees_mode == MyExchange.FEES_MODE_FORWARD:
            price_diff = sell_price * (1.0 - sell_fee_ratio) \
                       - buy_price / (1.0 - buy_fee_ratio) \
                       - buy_price * fee_ratio \
                       - delta_sell2buy
        else:
            price_diff = sell_price * (1.0 - sell_fee_ratio) \
                       - buy_price * (1.0 + buy_fee_ratio) \
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
    global g_real_arbit_diff
    arbit_diff = g_real_arbit_diff
    result = {}

    a = myex_a
    b = myex_b

    if get_param('G_PARAM_IGNORE_LAST_DIFF'):
        ab_ld = 0.0
        ba_ld = 0.0
    else:
        ab_ld = get_alltk_status(a.name, 'last_diff', b.name, 'tune', 'value')
        ba_ld = get_alltk_status(b.name, 'last_diff', a.name, 'tune', 'value')

    a_sell_price = a.get_buy1_price() - slip_point
    a_buy_price = a.get_sell1_price() + slip_point

    b_sell_price = b.get_buy1_price() - slip_point
    b_buy_price = b.get_sell1_price() + slip_point

    if a_sell_price <= 0.0 or a_buy_price <= 0.0 or \
       b_sell_price <= 0.0 or b_buy_price <= 0.0:
        return None

    last_price_diff = a.get_last_price() - b.get_last_price()

    # 如果当前最后成交差价达到了最大差价的 70% 以上，可以扩大套利差
    max_diff = abs(get_param('G_PARAM_MAX_DIFF'))
    if max_diff > 0.0 and abs(last_price_diff) > max_diff * 0.7:
        arbit_diff *= 1.0 + abs(last_price_diff) / max_diff

    # 为了确保执行设定的套利差起到了实际的作用，计算的时候需要按精度凑整
    a_diff = caculate_price_diff(round_sell_price(a_sell_price), a.trdfee['Sell'],
                                 round_buy_price(b_buy_price), b.trdfee['Buy'],
                                 arbit_diff,
                                 ab_ld,
                                 b.fees_mode)
    b_diff = caculate_price_diff(round_sell_price(b_sell_price), b.trdfee['Sell'],
                                 round_buy_price(a_buy_price), a.trdfee['Buy'],
                                 arbit_diff,
                                 ba_ld,
                                 a.fees_mode)

    if a_diff > 0:
        # a卖b买
        result['sell_myex'] = a
        result['sell_price'] = a_sell_price
        result['buy_myex'] = b
        result['buy_price'] = b_buy_price
        result['delta'] = ab_ld
        result['diff'] = a_diff
        result['direction'] = 'asbb'
    elif b_diff > 0:
        # a买b卖
        result['sell_myex'] = b
        result['sell_price'] = b_sell_price
        result['buy_myex'] = a
        result['buy_price'] = a_buy_price
        result['delta'] = ba_ld     # NOTE: 这里使用 -delta, 原版为 delta
        result['diff'] = b_diff
        result['direction'] = 'abbs'
    else:
        result = None

    return result

def calc_arbit_sell_amount(buy_amount, buy_fee_ratio, fees_mode):
    '''在某种费率模式下，套利卖的数量需要比买的数量要少一点'''
    if fees_mode == MyExchange.FEES_MODE_FORWARD:
        sell_amount = buy_amount * (1.0 - buy_fee_ratio)
    else:
        sell_amount = buy_amount
    return sell_amount

def need_update_depth(myex_list, myex_comp_list):
    '''
    需要深度信息的情形
        (1) 可以套利时
        (2) 可以平仓时
    '''
    # {myex.name: True/False, ...}
    result = {}

    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
    slip_point = get_param('G_PARAM_SLIP_POINT')
    tick = get_loop_count()

    for myex in myex_list:
        result[myex.name] = False

    # @ 可能套利的
    for (myex_a, myex_b) in myex_comp_list:
        if myex_a.ticker_tick != tick or myex_b.ticker_tick != tick:
            continue

        ret = caculate_arbitrage(myex_a, myex_b, slip_point)
        if not ret:
            continue

        if ret['direction'] == 'asbb':
            max_order_sell_amount = myex_a.get_max_order_sell_amount()
            max_order_buy_amount = myex_b.get_max_order_buy_amount(ret['buy_price'])
            arbit_sell_amount = calc_arbit_sell_amount(max_order_buy_amount,
                                                       myex_b.buy_fee_ratio,
                                                       myex_b.fees_mode)
            if min(max_order_sell_amount,
                   max_order_buy_amount,
                   arbit_sell_amount) >= min_trade_amount:
                result[myex_a.name] = True
                result[myex_b.name] = True
        elif ret['direction'] == 'abbs':
            max_order_sell_amount = myex_b.get_max_order_sell_amount()
            max_order_buy_amount = myex_a.get_max_order_buy_amount(ret['buy_price'])
            arbit_sell_amount = calc_arbit_sell_amount(max_order_buy_amount,
                                                       myex_a.buy_fee_ratio,
                                                       myex_a.fees_mode)
            if min(max_order_sell_amount,
                   max_order_buy_amount,
                   arbit_sell_amount) >= min_trade_amount:
                result[myex_a.name] = True
                result[myex_b.name] = True

    # @ 可能重试平仓的
    for myex in myex_list:
        if result[myex.name]:
            continue
        if make_retry_arbit_close_orders(myex_list, myex, check=True):
            result[myex.name] = True

    # @ 可能强制平仓的
    nfc = need_force_close(myex_list)
    for myex in myex_list:
        if nfc or myex.is_pending_force():
            result[myex.name] = True

    return result

def clean_exchange_data(myex_list, loop_count):
    for myex in myex_list:
        myex.clean_data()

def wait_async_thread(async_list):
    tick = get_loop_count()
    for dic in async_list:
        myex = dic['myex']
        td = dic['thread']
        method = dic['method']
        t0 = dic['time']
        try:
            ret, ok = td.wait(2000) # 最多等待 2000ms
        except:
            Log(traceback.format_exc())
            continue
        if not ok:
            Log('[%s] %s 超时' % (myex.name, method))
            continue
        if ret is None:
            Log('[%s] %s 失败' % (myex.name, method))
            continue
        myex.delay += (time.time() - t0) * 1000
        if method == 'GetAccount':
            account = bytes2str(ret)
            myex.account_refresh_state = 'refresh_complete'
            myex.account_update_tick = tick
            myex.account_tick = tick
            if myex.account != account:
                myex.account_change_tick = tick
            myex.account = account
        elif method == 'GetTicker':
            ticker = bytes2str(ret)
            myex.ticker_tick = tick
            for k in ('Sell', 'Buy', 'Last'): # 我们只用这 3 个值
                v = ticker.setdefault(k, 0.0)
                if not isinstance(v, (int, float)):
                    ticker[k] = 0.0
            myex.ticker = ticker
        elif method == 'GetDepth':
            depth = bytes2str(ret)
            myex.depth_tick = tick
            myex.depth = depth
        else:
            pass

def sync_fetch_exchange_data(myex_list, myex_comp_list, loop_count):
    # NOTE: 如果获取失败，保留上一次的数据，绝不会清空数据，这个原则很实用
    #       如果要标记数据是过时的，只需要一个变量即可达到
    for idx, myex in enumerate(myex_list): # Account
        if myex.account_refresh_state == 'refresh_instant' or \
           (myex.account_refresh_state == 'refresh_random' and \
            loop_count % 60 == (59 - idx)): # 让交易所在不同的循环更新
            if not myex.will_update():
                continue
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
        if not myex.will_update():
            continue
        t0 = time.time()
        ret = myex.get_ticker()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.ticker_tick = loop_count

    depth_update_dict = need_update_depth(myex_list, myex_comp_list)
    for myex in myex_list: # Depth
        # 不需要每次轮询都获取深度信息
        if not depth_update_dict[myex.name]:
            continue
        t0 = time.time()
        ret = myex.get_depth()
        myex.delay += (time.time() - t0) * 1000
        if not ret is None:
            myex.depth_tick = loop_count

def async_fetch_exchange_data(myex_list, myex_comp_list, loop_count):
    enable_boost_async = get_param('G_PARAM_ENABLE_BOOST_ASYNC')
    account_async_list = []
    ticker_async_list = []
    depth_async_list = []

    # 状态为立即更新 或者 到了随机刷新的时候，才执行刷新
    # NOTE: 如果获取失败，保留上一次的数据，绝不会清空数据，这个原则很实用
    #       如果要标记数据是过时的，只需要一个变量即可达到
    for idx, myex in enumerate(myex_list): # Account
        if myex.account_refresh_state == 'refresh_instant' or \
           (myex.account_refresh_state == 'refresh_random' and \
            loop_count % 60 == (59 - idx)): # 让交易所在不同的循环更新
            if not myex.will_update():
                continue
            account_async_list.append(myex.Go('GetAccount'))
        else:
            myex.account_tick = loop_count

    if not enable_boost_async:
        wait_async_thread(account_async_list)

    for myex in myex_list: # Ticker
        if not myex.will_update():
            continue
        ticker_async_list.append(myex.Go('GetTicker'))

    if enable_boost_async:
        wait_async_thread(account_async_list)

    wait_async_thread(ticker_async_list)

    depth_update_dict = need_update_depth(myex_list, myex_comp_list)
    for myex in myex_list: # Depth
        # 不需要每次轮询都获取深度信息
        if not depth_update_dict[myex.name]:
            continue
        depth_async_list.append(myex.Go('GetDepth'))

    wait_async_thread(depth_async_list)

def fetch_exchange_data(myex_list, myex_comp_list, loop_count):
    if get_param('G_PARAM_ENABLE_ASYNC_MODE'):
        return async_fetch_exchange_data(myex_list, myex_comp_list, loop_count)
    else:
        return sync_fetch_exchange_data(myex_list, myex_comp_list, loop_count)

def generate_compare_list(myex_list):
    li = []
    ll = len(myex_list) - 1
    for i in range(ll):
        for j in range(ll - i):
            li.append((myex_list[i], myex_list[i+j+1]))
    return li

def float_round_up(f, prec):
    assert isinstance(prec, int)
    assert prec >= 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_UP))

def float_round_down(f, prec):
    assert isinstance(prec, int)
    assert prec >= 0
    if prec == 0:
        return int(f)
    s = '0.' + '0' * (prec-1) + '1'
    return float(decimal.Decimal(f).quantize(decimal.Decimal(s),
                                             rounding=decimal.ROUND_DOWN))

def round_buy_price(buy_price):
    return float_round_up(buy_price, get_param('G_PARAM_PRICE_PREC'))

def round_sell_price(sell_price):
    return float_round_down(sell_price, get_param('G_PARAM_PRICE_PREC'))

def round_up_price(price):
    return float_round_up(price, get_param('G_PARAM_PRICE_PREC'))

def round_down_price(price):
    return float_round_down(price, get_param('G_PARAM_PRICE_PREC'))

def round_amount(amount):
    return float_round_down(amount, get_param('G_PARAM_AMOUNT_PREC'))

def _caculate_position_offset(stocks, balance, last_price):
    '''
    计算仓位偏移, 以最后成交价（现价）计算, 不考虑冻结的资产, 不考虑手续费

    base : quote
    1 : 1 的偏移为 0%
    1.5 : 0.5 -> -50%
    0.5 : 1.5 -> +50% / 50%
    1.9 : 0.1 -> -90%
    0.9 : 1.1 -> +10% / 10%

    @return
        百分率, 如 1.5 : 0.5 则返回 -50.0
    '''
    if not last_price:
        return 0.0
    # 00, 01, 10, 11
    if not stocks and not balance:
        return 0.0
    elif not stocks and balance:
        return 100.0
    elif stocks and not balance:
        return -100.0

    max_balance = balance + stocks * last_price
    mid_balance = max_balance / 2.0
    if not mid_balance:
        return -100.0
    offset = balance / mid_balance * 100.0 - 100.0

    return offset

def caculate_all_position_offset(stocks):
    # -inf < offset <= 100.0
    global g_all_init_fund
    if get_all_base_stocks() <= 0.0:
        return 100.0
    offset = (stocks / get_all_base_stocks() * 100.0 - 100.0)
    # 这个偏移只要取一定精度的结果就好了
    offset = float_round_down(offset, 2)
    if offset == 0.0:
        offset = 0.0    # 避免显示 -0.00
    else:
        offset = -offset
    return offset

def get_canceled_buy_list(myex_list, myex):
    global g_arbit_status
    canceled_buy_list = []
    for a_name, dic in g_arbit_status.items():
        if a_name == myex.name:
            continue
        status = dic[myex.name]['canceled']
        if status['buy']['amount'] <= 0.0:
            continue
        pair_info = {'sell_myex': get_myex_by_name(a_name, myex_list),
                     'buy_myex': myex}
        item = {'pair_info': pair_info}
        item['buy'] = status['buy']
        canceled_buy_list.append(item)
    return canceled_buy_list

def get_canceled_sell_list(myex_list, myex):
    # 取出所有的组合，做成列表，amount 为 0.0 的不包括在内
    # pair_info : {'sell_myex': x, 'buy_myex': y}
    # item = {'sell'/'buy': {'amount': 1.0, 'volume': 1.0}, 'pair_info': {}}
    global g_arbit_status
    canceled_sell_list = []
    for b_name, status in g_arbit_status[myex.name].items():
        status = status['canceled']
        if status['sell']['amount'] <= 0.0:
            continue
        pair_info = {'sell_myex': myex,
                     'buy_myex': get_myex_by_name(b_name, myex_list)}
        item = {'pair_info': pair_info}
        item['sell'] = status['sell']
        canceled_sell_list.append(item)
    return canceled_sell_list

def make_retry_arbit_close_orders(myex_list, myex, check=False):
    '''
    重试套利平仓（这是由于某次搬砖未能完全成交导致，对比失败的vwap）

    order = {
        'aim': aim,
        'type': 'buy'/'sell',
        'price': x,
        'amount': y,
        'myex': myex,
    }

    @return
        空列表或1个order或2个order
    '''
    result = []
    if check and myex.ticker_tick != get_loop_count():
        return False

    canceled_buy_list = get_canceled_buy_list(myex_list, myex)
    canceled_sell_list = get_canceled_sell_list(myex_list, myex)

    # 按照 vwap 排序
    canceled_sell_list.sort(key=lambda x: x['sell']['volume']/x['sell']['amount'], reverse=False)
    canceled_buy_list .sort(key=lambda x: x['buy']['volume']/x['buy']['amount'], reverse=True)

    if not canceled_buy_list and not canceled_sell_list:
        return []

    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')

    if not check and canceled_buy_list and canceled_sell_list:
        buy1 = canceled_buy_list[0]['buy']
        sell1 = canceled_sell_list[0]['sell']
        buy1_vwap = buy1['volume'] / buy1['amount']
        sell1_vwap = sell1['volume'] / sell1['amount']
        pub_amount = min(buy1['amount'], sell1['amount'])
        # 重试会导致亏损的交易，我们不需要重试，自己撮合即可，还能获得额外的利润
        if buy1_vwap >= sell1_vwap:
            a_name = canceled_buy_list[0]['pair_info']['sell_myex'].name
            myex_b = canceled_buy_list[0]['pair_info']['buy_myex']
            b_name = myex_b.name
            buy_amount = pub_amount
            if myex_b.fees_mode == myex_b.FEES_MODE_FORWARD:
                buy_amount /= (1.0 - myex_b.buy_fee_ratio)
            update_arbit_buy_stats(a_name, b_name, 'canceled', buy1_vwap, buy_amount, sub=True)

            a_name = canceled_sell_list[0]['pair_info']['sell_myex'].name
            b_name = canceled_sell_list[0]['pair_info']['buy_myex'].name
            update_arbit_sell_stats(a_name, b_name, 'canceled', sell1_vwap, pub_amount, sub=True)

            # NOTE: hacked!
            #buy1['amount'] -= pub_amount
            #buy1['volume'] -= buy1_vwap * pub_amount
            #sell1['amount'] -= pub_amount
            #sell1['volume'] -= sell1_vwap * pub_amount
            # 从手续费赚的(都转为 balance 了)：
            #   - buy1_vwap * pub_amount * buy_fee_ratio
            #   - sell1_vwap * pub_amount * buy_fee_ratio
            # profit 包含了手续费，负数的绝对值更大了
            # earn = sell1_vwap * pub_amount * (1-fee)
            # cost = buy1_vwap * pub_amount / (1-fee)
            # e - c = (sell1_vwap*(1-fee) - buy1_vwap/(1-fee)) * pub_amount
            profit = (sell1_vwap - buy1_vwap) * pub_amount
            myex.add_raw_stats('cancel.arbit.profit', profit)

            return []

    # 不是最新的信息，不执行
    if not check and not myex.is_latest():
            return []

    buy1_price = myex.get_buy1_price()
    buy1_amount = myex.get_buy1_amount()
    sell1_price = myex.get_sell1_price()
    sell1_amount = myex.get_sell1_amount()

    for i in canceled_buy_list:
        item = i['buy']
        order_amount = item['amount']
        if myex.fees_mode == myex.FEES_MODE_FORWARD:
            # 修正手续费导致的数量变化，需要多买一点才行
            order_amount = item['amount'] / (1.0 - myex.buy_fee_ratio)
        # 平仓的价格，我们避免亏损，需要按照利润方向凑整
        buy_vwap = round_down_price(item['volume'] / item['amount'])
        target_buy_amount = min(order_amount,
                                myex.get_max_order_buy_amount(buy_vwap))
        if check:
            if buy_vwap >= sell1_price and target_buy_amount >= min_trade_amount:
                return True
            else:
                continue
        target_buy_amount = min(sell1_amount, target_buy_amount)
        if buy_vwap >= sell1_price and target_buy_amount >= min_trade_amount:
            order = {
                'aim': 'close_retry_arbit',
                'type': 'buy',
                'price': buy_vwap,
                'amount': target_buy_amount,
                'myex': myex,
                # 这种类型特有
                'pair_info': i['pair_info'],
            }
            result.append(order)
            break # 简单处理，只下一个买单

    for i in canceled_sell_list:
        item = i['sell']
        # 平仓的价格，我们避免亏损，需要按照利润方向凑整
        sell_vwap = round_up_price(item['volume'] / item['amount'])
        target_sell_amount = min(item['amount'],
                                 myex.get_max_order_sell_amount())
        if check:
            if sell_vwap <= buy1_price and target_sell_amount >= min_trade_amount:
                return True
            else:
                continue
        target_sell_amount = min(target_sell_amount, buy1_amount)
        if sell_vwap <= buy1_price and target_sell_amount >= min_trade_amount:
            order = {
                'aim': 'close_retry_arbit',
                'type': 'sell',
                'price': sell_vwap,
                'amount': target_sell_amount,
                'myex': myex,
                # 这种类型特有
                'pair_info': i['pair_info'],
            }
            result.append(order)
            break

    if check:
        return False
    return result

def get_all_base_stocks():
    '''获取基准的 stocks，即平仓状态下的 stocks
    用于以后实现增长的 base stocks'''
    global g_myex_list
    global g_all_init_fund
    if get_param('G_PARAM_EXCHANGE_BASE_STOCKS').strip():
        # 如果使用了策略参数，则以策略参数为准
        all_base_stocks = sum([myex.base_stocks for myex in g_myex_list])
    else:
        # 如果没有使用策略参数，则以初始资金的 stocks 为准，这个可能会被设置
        all_base_stocks = g_all_init_fund['stocks']
    return all_base_stocks

def get_all_offset(myex_list):
    all_fund = get_all_fund(myex_list)
    all_offset = caculate_all_position_offset(all_fund['Stocks'] + all_fund['FrozenStocks'])
    return all_offset

def _make_force_close_order_by_pending(myex):
    '''
    由于浮点的误差问题，强制平仓后，仓位可能跟真正的平仓仓位有一点差距
    '''
    if not myex.is_latest():
        return None

    order = {}
    price_threshold = 5
    buy_or_sell = ''
    target_price = 0.0
    last_price = myex.get_last_price()
    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')

    if not myex.is_pending_force():
        return None
    if last_price <= 0.0:
        return None

    if myex.pending_force['amount'] < min_trade_amount:
        Log('[%s] 剩余的强制平仓量 %.*f 低于最小成交量，忽略并清零。'
            % (myex.name, myex.amount_prec,
               round_amount(myex.pending_force['amount'])))
        myex.reset_pending_force()
        return None

    if myex.pending_force['type'] == 'buy':
        # buy
        buy_price = myex.get_sell1_price()
        # 求稳不求利，当前价位浮动过于剧烈的话就先不买卖
        if abs(buy_price / last_price * 100.0 - 100.0) > price_threshold:
            Log('强制平仓买价为 %.*f，现价为 %.*f，差价 > %.2f%%，暂不平仓'
                % (myex.price_prec, buy_price,
                   myex.price_prec, last_price, price_threshold))
            return None
        buy_or_sell = 'buy'
        target_price = buy_price
        target_amount = min(myex.get_sell1_amount(), myex.pending_force['amount'])
        target_amount = min(target_amount, myex.get_max_order_buy_amount(target_price))
    else:
        # sell
        sell_price = myex.get_buy1_price()
        # 求稳不求利，当前价位浮动过于剧烈的话就先不买卖
        if abs(sell_price / last_price * 100.0 - 100.0) > price_threshold:
            Log('强制平仓卖价为 %.*f，现价为 %.*f，差价 > %.2f%%，暂不平仓'
                % (myex.price_prec, sell_price,
                   myex.price_prec, myex.ticker['Last'], price_threshold))
            return None
        buy_or_sell = 'sell'
        target_price = sell_price
        target_amount = min(myex.get_buy1_amount(), myex.pending_force['amount'])
        target_amount = min(target_amount, myex.get_max_order_sell_amount())

    if target_amount < min_trade_amount:
        return None

    order = {
        'type': buy_or_sell,
        'price': target_price,
        'amount': target_amount,
        'myex': myex,
        'aim': 'close_force',
    }

    return order

def make_force_close_orders_by_pending(myex_list):
    result = []
    for myex in myex_list:
        order = _make_force_close_order_by_pending(myex)
        if order:
            result.append(order)
    return result

def need_force_close(myex_list):
    if get_param('G_PARAM_ENABLE_FORCE_CLOSE') and \
       abs(get_all_offset(myex_list)) > get_param('G_PARAM_FORCE_CLOSE_OFFSET_THRESHOLD'):
        return True
    return False

def make_force_close_orders(myex_list):
    '''
    最简单粗暴的平仓方式，根据与初始的仓位对比，偏移了多少就直接平仓多少
    只有所有的交易所的强制平仓完成后，才会执行下一次强制平仓
    如果由于余额或者余币不足无法全部完成平仓，那就是只能认倒霉了
    '''
    result = []
    is_pending_force = False
    for myex in myex_list:
        if myex.is_pending_force():
            is_pending_force = True
    result += make_force_close_orders_by_pending(myex_list)
    if is_pending_force or result:
        return result

    if not need_force_close(myex_list):
        return None

    Log('开始执行强制平仓...')

    all_fund = get_all_fund(myex_list)
    stocks_diff = all_fund['stocks'] - get_all_base_stocks()
    if stocks_diff == 0.0:
        return None

    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
    # 确保总资金量达到一定规模，设置的仓位强制平仓阈值正确就不会出现此情况
    if abs(stocks_diff) < min_trade_amount:
        return None

    try:
        if stocks_diff > 0.0:
            # 需要卖一些，按剩余的 stocks 等比去卖
            for myex in myex_list:
                ratio = myex.account['Stocks'] / all_fund['Stocks']
                target_amount = stocks_diff * ratio
                if target_amount < min_trade_amount:
                    continue
                myex.pending_force['type'] = 'sell'
                myex.pending_force['amount'] = target_amount
        else:
            # FIXME: 如果为 FEES_MODE_FORWARD 模式，需要下单得跟多一点
            #        这个版本我们暂时不处理
            # 需要买一些，按剩余的 balance 等比去买
            for myex in myex_list:
                ratio = myex.account['Balance'] / all_fund['Balance']
                target_amount = abs(stocks_diff) * ratio
                if target_amount < min_trade_amount:
                    continue
                myex.pending_force['type'] = 'buy'
                myex.pending_force['amount'] = target_amount
    except ZeroDivisionError:
        Log('总商品币或总定价币为 0.0，无法强制平仓。all_fund = %s' % all_fund)

    reset_all_canceled_status(myex_list)

    result += make_force_close_orders_by_pending(myex_list)

    return result

def make_close_orders(myex_list):
    '''
    *** 每回合只进行一种平仓方式 ***
    计算平仓交易订单
        - 初始平仓 (close_initi)                    # 暂时不实现，开始时检测防止出现这种情况
        - 强制平仓 (close_force)
        - 重试套利平仓 (close_retry_arbit)
        - 对称套利平仓 (close_arbit_reverse)        # 暂时不实现
        - 重试对称平仓 (close_retry_arbit_reverse)  # 暂时不实现

    数据结构
        order = {
            'aim': aim,
            'type': 'buy'/'sell',
            'price': x,
            'amount': y,
            'myex': myex,
            'pair_info': {}; # 'aim' == 'close_retry_arbit'
        }
    '''
    result = []

    # @ 优先强制平仓
    orders = make_force_close_orders(myex_list)
    if orders:
        result += orders
    if result:
        return result

    # @ 如果当前价格合适, 即执行重试平仓
    for myex in myex_list:
        orders = make_retry_arbit_close_orders(myex_list, myex)
        if orders:
            result += orders
    if result:
        return result

    return result

def process_close_orders(all_close_orders):
    result = 0
    for order in all_close_orders:
        myex = order['myex']
        amount = round_amount(order['amount'])
        otype = order['type']
        if otype == 'buy':
            price = round_buy_price(order['price'])
            ret = myex.buy(price, amount)
        else:
            price = round_sell_price(order['price'])
            ret = myex.sell(price, amount)
        if ret is None:
            Log('[%s] 下单失败：%s(%.*f, %.*f)'
                % (myex.name, otype,
                   myex.price_prec, price,
                   myex.amount_prec, amount))
            continue
        Log('[%s] 策略执行了平仓交易 %s(%.*f, %.*f) = %s'
            % (myex.name, otype,
               myex.price_prec, price,
               myex.amount_prec, amount,
               repr(ret)))
        result += 1
        myex.add_stats('order', order['aim'], otype, 'count', 1)
        myex.add_stats('order', order['aim'], otype, 'amount', amount)
        info = {
            'id_type': type(ret).__name__,
            'type': order['type'],
            'aim': order['aim'],
            'price': price,
            'amount': amount,
            'tick': get_loop_count(),
        }

        if order['aim'] == 'close_retry_arbit':
            info['pair_info'] = order['pair_info']
            a_name = order['pair_info']['sell_myex'].name
            b_name = order['pair_info']['buy_myex'].name
            if order['type'] == 'buy':
                update_arbit_buy_stats(a_name, b_name, 'canceled', price, amount, sub=True)
            else:
                update_arbit_sell_stats(a_name, b_name, 'canceled', price, amount, sub=True)
        elif order['aim'] == 'close_force':
            myex.pending_force['amount'] -= amount

        myex.executed_orders[str(ret)] = info
    return result

def close_the_position(myex_list):
    '''
    @return
        平仓下单数量（非交易数量）, None 表示未达成平仓条件
    '''
    all_close_orders = make_close_orders(myex_list)
    ret = process_close_orders(all_close_orders)

    return ret

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

    max_trade_amount 已经包含 trade['amount'] 的信息了
    return 买单id，卖单id，买入数量，卖出数量
    '''
    sell_myex = trade['sell_myex']
    buy_myex = trade['buy_myex']
    min_trade_amount = get_param('G_PARAM_MIN_TRADE_AMOUNT')
    if max_trade_amount < min_trade_amount:
        Log('本轮套利中，前几次的套利交易已经用尽了资金，放弃此次套利。')
        LogDebug(json.dumps(norm4json(trade)))
        return None, None, 0.0, 0.0

    target_amount = max(trade['strategy_amount'], min_trade_amount)
    target_amount = min(target_amount, max_trade_amount)

    target_buy_amount = round_amount(target_amount)
    if buy_myex.fees_mode == buy_myex.FEES_MODE_FORWARD:
        target_sell_amount = target_amount * (1.0 - buy_myex.trdfee['Buy'] / 100.0)
    else:
        target_sell_amount = target_amount
    target_sell_amount = round_amount(target_sell_amount)
    bsmin_amount = min(target_buy_amount, target_sell_amount)
    if bsmin_amount < min_trade_amount:
        # 最小交易量统一在制作订单的时候检查了，所以这里应该很少可能打印
        LogDebug('该次交易数量 min(%.*f, %.*f) 少于策略设置的最小交易量 %.*f，放弃执行交易。'
                 % (buy_myex.amount_prec, target_buy_amount,
                    sell_myex.amount_prec, target_sell_amount,
                    buy_myex.amount_prec, min_trade_amount))
        return None, None, 0.0, 0.0

    target_buy_price = round_buy_price(trade['buy_price'])
    target_sell_price = round_sell_price(trade['sell_price'])

    # NOTE: 这里先计算，可能由于小数截断的问题，收益变为负的
    earn = sell_myex.calc_earn(target_sell_price, target_sell_amount)
    cost = buy_myex.calc_cost(target_buy_price, target_buy_amount)
    arbitrage_profit = earn - cost
    if arbitrage_profit <= 0.0:
        # sell(0.003542, 0.99) - buy(0.003521, 1.00) = -0.000021
        LogDebug(("由于误差导致负收益，放弃此次套利：%s.sell(%.*f, %.*f) - " +
                  "%s.buy(%.*f, %.*f) = %.*f")
                 % (sell_myex.name,
                    sell_myex.price_prec, target_sell_price,
                    sell_myex.amount_prec, target_sell_amount,
                    buy_myex.name,
                    buy_myex.price_prec, target_buy_price,
                    buy_myex.amount_prec, target_buy_amount,
                    sell_myex.price_prec, arbitrage_profit))
        return None, None, 0.0, 0.0

    # @ 买入
    buy_order_id = buy_myex.buy(target_buy_price, target_buy_amount)
    if buy_order_id is None:
        Log('[%s] 下单失败：以 %.*f 价格买入 %.*f %s，取消此次套利交易'
            % (buy_myex.name, buy_myex.price_prec, target_buy_price,
               buy_myex.amount_prec, target_buy_amount, buy_myex.base))
        #update_arbit_buy_stats(sell_myex.name, buy_myex.name, 'canceled',
                               #target_buy_price, target_buy_amount)
        return None, None, 0.0, 0.0
    else:
        buy_myex.executed_orders[str(buy_order_id)] = {
            'id_type': type(buy_order_id).__name__,
            'type': 'buy',
            'aim': 'arbit',
            'price': target_buy_price,
            'amount': target_buy_amount,
            'tick': get_loop_count(),
            'pair_myex': sell_myex,     # 记录配对的信息
        }
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()
        buy_myex.add_stats('order', 'arbit', 'buy', 'amount', target_buy_amount)
        buy_myex.add_stats('order', 'arbit', 'buy', 'count', 1)
        update_arbit_buy_stats(sell_myex.name, buy_myex.name, 'executed',
                               target_buy_price, target_buy_amount)
        # 第一个订单下单成功立即认为这个套利已经执行，万一另一个单下单失败
        # 添加下一个单的取消记录即可
        update_arbit_sell_stats(sell_myex.name, buy_myex.name, 'executed',
                                target_sell_price, target_sell_amount)

    # @ 卖出
    sell_order_id = sell_myex.sell(target_sell_price, target_sell_amount)
    if sell_order_id is None:
        Log('下单失败：以 %.*f 价格卖出 %.*f %s，但是套利买单已经下单成功...'
            % (sell_myex.price_prec, target_sell_price,
               sell_myex.amount_prec, target_sell_amount, sell_myex.base))
        update_arbit_sell_stats(sell_myex.name, buy_myex.name, 'canceled',
                                target_sell_price, target_sell_amount)
        # 下单失败也要继续
        #return buy_order_id, None, target_buy_amount, target_sell_amount
    else:
        sell_myex.executed_orders[str(sell_order_id)] = {
            'id_type': type(sell_order_id).__name__,
            'type': 'sell',
            'aim': 'arbit',
            'price': target_sell_price,
            'amount': target_sell_amount,
            'tick': get_loop_count(),
            'pair_myex': buy_myex,
        }
        buy_myex.executed_orders[str(buy_order_id)]['pair_oid'] = sell_order_id
        touch_last_arbitrage_timestamp()
        touch_last_order_timestamp()
        sell_myex.add_stats('order', 'arbit', 'sell', 'amount', target_sell_amount)
        sell_myex.add_stats('order', 'arbit', 'sell', 'count', 1)

    if not buy_order_id is None and not sell_order_id is None:
        Log('本次理论套利收益:', arbitrage_profit)
        add_stats('STATS_ARBITRAGE_PROFIT', arbitrage_profit)

    return buy_order_id, sell_order_id, target_buy_amount, target_sell_amount

def process_arbitrage_trades(myex_list, all_trade_list):
    '''
    返回交易数量
    '''
    if not all_trade_list:
        return 0.0

    total_trade_amount = 0.0
    sorted_list = sorted(all_trade_list, key=lambda k: k['diff'], reverse=True)

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
        # 减掉之前交易冻结的资金
        balance = buy_myex.account['Balance'] - frozen_fund[buy_myex.name]['total_frozen_balance']
        stocks = sell_myex.account['Stocks'] - frozen_fund[sell_myex.name]['total_frozen_stocks']

        # 这里不算与 buy_myex 套利而缩减后的数量，因为 process_arbitrage_trade 会处理
        max_sell_amount = stocks
        # 必须算上手续费，否则可能出现错误结果
        max_buy_amount = buy_myex.get_max_order_buy_amount(trade['buy_price'],
                                                           Balance=balance)
        max_trade_amount = min(max_buy_amount,
                               max_sell_amount,
                               trade['amount'])
        if max_trade_amount < get_param('G_PARAM_MIN_TRADE_AMOUNT'):
            continue

        # 开始交易
        buy_order_id, sell_order_id, buy_amount, sell_amount = \
                process_arbitrage_trade(trade, max_trade_amount)
        if buy_order_id is None and sell_order_id is None:
            # 很倒霉，这次套利交易因故不能执行，原因 process_arbitrage_trade 函数已经打印
            #LogDebug('该次套利交易因故不能执行：%s' % trade)
            continue

        if not buy_order_id is None:
            frozen_fund[buy_myex.name]['total_frozen_balance'] += \
                    buy_myex.calc_cost(trade['buy_price'], buy_amount)
        if not sell_order_id is None:
            frozen_fund[sell_myex.name]['total_frozen_stocks'] += sell_amount

        if buy_order_id is None or sell_order_id is None:
            if not buy_order_id is None:
                Log('该次套利只成功下单买单，下单卖单失败，等待取消订单...')
            else:
                Log('该次套利只成功下单卖单，下单买单失败，等待取消订单...')
            continue

        total_trade_amount += min(buy_amount, sell_amount)

    return total_trade_amount

def tune_arbit_diff(last_trade_amount):
    '''
    调整套利差, 套利差为百分数 0.25 -> 0.25%
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
    global g_real_arbit_diff
    result = False
    base_trade_amount = get_param('G_PARAM_BASE_TRADE_AMOUNT')
    min_ad = get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN')
    max_ad = get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MAX')
    prev_arbit_diff = g_real_arbit_diff

    if last_trade_amount > base_trade_amount * 25 and \
         last_trade_amount < base_trade_amount * 50:
        pass
    else:
        if   last_trade_amount < base_trade_amount:
            g_real_arbit_diff -= 0.004
        elif last_trade_amount < base_trade_amount * 20:
            g_real_arbit_diff -= 0.001
        elif last_trade_amount > base_trade_amount * 100:
            g_real_arbit_diff += 0.015
        elif last_trade_amount > base_trade_amount * 50:
            g_real_arbit_diff += 0.002
        else:
            ## FIXME: 20x <= y < 50x 这种情况没处理? (结合25x < y < 50x)
            ## 实际为 20x <= y <= 25x 这种情况没有处理（不调整套利差）
            pass
        result = True

    old = g_real_arbit_diff
    # 无论怎么调整, 都不能超越上下限
    if g_real_arbit_diff < min_ad:
        g_real_arbit_diff = min_ad
    elif g_real_arbit_diff > max_ad:
        g_real_arbit_diff = max_ad
    if result and prev_arbit_diff != g_real_arbit_diff:
        LogDebug('最近的套利交易数量为: %.*f，套利差更新为: %.*f (%.*f)。'
            % (get_param('G_PARAM_AMOUNT_PREC'), last_trade_amount,
               4, g_real_arbit_diff, 4, old))

    return result

def clean_order_dict(myex, incompl_orders):
    '''
    只在字典里面保留 incompl_orders 存在的订单, 其他订单一律清理
    '''
    new_dict = {}
    for order in incompl_orders:
        oid = str(order['Id'])
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
            oid = str(order['Id'])
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

            incompl_amount = order['Amount'] - order['DealAmount']
            incompl_price = order['Price']
            volume = incompl_price * incompl_amount

            if not oinfo:
                Log('[%s] 未知订单:' % myex.name, order)
                myex.add_stats('cancel', 'unknown', 'buy', 'amount', incompl_amount)
                myex.add_stats('cancel', 'unknown', 'buy', 'count', 1)
                continue

            if oinfo['aim'] == 'arbit':
                if order['Type'] == ORDER_TYPE_BUY:
                    sell_myex = oinfo['pair_myex']
                    buy_myex = myex
                    update_arbit_buy_stats(sell_myex.name, buy_myex.name, 'canceled',
                                           incompl_price, incompl_amount)
                    #update_arbit_buy_stats(sell_myex.name, buy_myex.name, 'executed',
                                           #incompl_price, incompl_amount, sub=True)
                else:
                    sell_myex = myex
                    buy_myex = oinfo['pair_myex']
                    update_arbit_sell_stats(sell_myex.name, buy_myex.name, 'canceled',
                                            incompl_price, incompl_amount)
                    #update_arbit_sell_stats(sell_myex.name, buy_myex.name, 'executed',
                                            #incompl_price, incompl_amount, sub=True)
            elif oinfo['aim'] == 'close_retry_arbit':
                sell_myex = oinfo['pair_info']['sell_myex']
                buy_myex = oinfo['pair_info']['buy_myex']
                if order['Type'] == ORDER_TYPE_BUY:
                    update_arbit_buy_stats(sell_myex.name, buy_myex.name, 'canceled',
                                           incompl_price, incompl_amount)
                else:
                    update_arbit_sell_stats(sell_myex.name, buy_myex.name, 'canceled',
                                            incompl_price, incompl_amount)
            elif oinfo['aim'] == 'close_force':
                myex.pending_force['amount'] += incompl_amount
                # 需要根据取消的订单重置 pending_force 的 'type' 吗？

            if order['Type'] == ORDER_TYPE_BUY:
                myex.add_stats('cancel', oinfo['aim'], 'buy', 'amount', incompl_amount)
                myex.add_stats('cancel', oinfo['aim'], 'buy', 'count', 1)
            elif order['Type'] == ORDER_TYPE_SELL:
                myex.add_stats('cancel', oinfo['aim'], 'sell', 'amount', incompl_amount)
                myex.add_stats('cancel', oinfo['aim'], 'sell', 'count', 1)
            else:
                Log('WTF on Cancel Order!', order)

    return incompl_order_count

def _draw_table(*tables):
    global g_run_on_botvs
    if not tables:
        return

    if g_run_on_botvs:
        LogStatus('`' + '`\n`'.join(map(json.dumps, tables)) + '`')
        return

    ts = []
    for table in tables:
        if isinstance(table, list):
            for t in table:
                ts.append(t)
        else:
            ts.append(table)

    import texttable
    prec = max(get_param('G_PARAM_PRICE_PREC'), get_param('G_PARAM_AMOUNT_PREC'))
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

def calc_real_arbit(all_init_fund, all_curr_fund):
    real_arbit_profilt = (all_curr_fund['stocks'] - all_init_fund['stocks']) \
                        * all_curr_fund['price'] \
                        + all_curr_fund['balance'] - all_init_fund['balance']
    return real_arbit_profilt

def refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms):
    global g_startup_time
    global g_real_arbit_diff
    global g_version
    if not myex_list:
        return

    tables = []
    # 显示的信息可以按照设置的精度显示，所以不保证显示的信息很准确
    price_prec = get_param('G_PARAM_PRICE_PREC')
    amount_prec = get_param('G_PARAM_AMOUNT_PREC')

    base = myex_list[0].base
    quote = myex_list[0].quote

    init_offset = caculate_all_position_offset(all_init_fund['stocks'])
    curr_offset = get_all_offset(myex_list)

    table_baseinfo = {
        'type': 'table',
        'title': '基础信息',
        'rows': [],
        'cols': [
            '策略版本',
            '开始时间',
            '当前时间',
            '交易对',
            '套利差(%)',
            '操作总延时(ms)',
        ]
    }
    row1 = [
        g_version,
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
            #'状态',

            '可用%s' % base,
            '冻结%s' % base,
            '可用%s' % quote,
            '冻结%s' % quote,
            '偏移(%)',

            '均价(%s)' % quote,
            '变化(%)',

            # 市值用最后成交价计算
            '市值(%s)' % quote,
            '变化(%)',

            '理论套利(%s)' % quote,
            '实际套利(%s)' % quote,
            '套利收益率(%)',
        ],
        'rows': [],
    }

    #table_summary['cols'] = ['x'] * len(table_summary['cols'])

    # 初始信息
    row1 = [
        #'初始',

        '%.*f' % (amount_prec, all_init_fund['Stocks']),
        '%.*f' % (amount_prec, all_init_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_init_fund['Balance']),
        '%.*f' % (price_prec, all_init_fund['FrozenBalance']),
        '%7.2f' % init_offset,

        '%.*f' % (price_prec, all_init_fund['price']),
        'N/A',

        '%.*f' % (price_prec, all_init_fund['total']),
        'N/A',

        'N/A',
        'N/A',
        'N/A',
    ]

    total_profit = all_curr_fund['total'] - all_init_fund['total']
    arbit_profit = get_stats('STATS_ARBITRAGE_PROFIT')
    real_arbit_profilt = calc_real_arbit(all_init_fund, all_curr_fund)
    row2 = [
        #'现在',

        '%.*f' % (amount_prec, all_curr_fund['Stocks']),
        '%.*f' % (amount_prec, all_curr_fund['FrozenStocks']),
        '%.*f' % (price_prec, all_curr_fund['Balance']),
        '%.*f' % (price_prec, all_curr_fund['FrozenBalance']),
        '%7.2f' % curr_offset,
        '%.*f' % (price_prec, all_curr_fund['price']),
        '%.*f' % (4, all_curr_fund['price']/all_init_fund['price']*100.0-100.0),

        # 市值
        '%.*f' % (price_prec, all_curr_fund['total']),
        # 市值变化
        '%.*f' % (4, total_profit / all_init_fund['total'] * 100.0),

        # 套利
        '%.*f' % (price_prec, arbit_profit),
        # 实际套利，以当前均价平衡仓位看余额差
        '%.*f' % (price_prec, real_arbit_profilt),
        # 套利收益率
        '%.*f' % (4, real_arbit_profilt / all_curr_fund['total'] * 100.0),
    ]

    assert len(table_summary['cols']) == len(row1)
    assert len(table_summary['cols']) == len(row2)
    table_summary['rows'].append(row1)
    table_summary['rows'].append(row2)

    table_exchange_dynamic = {
        'type': 'table',
        'title': '交易所动态信息',
        # headers
        'cols': [
            '交易所',
            '延时(ms)',

            '买1价',
            '卖1价',
            '现价',

            '可用%s' % base,
            '冻结%s' % base,
            '可用%s' % quote,
            '冻结%s' % quote,

            '可购%s' % base,
            '偏移(%)',
        ],
        'rows': [],
    }

    for myex in myex_list:
        try:
            # NOTE: 可购量用 卖1 价格计算
            max_buy_amount_mesg = '%.*f' % (myex.amount_prec,
                                            myex.get_max_order_buy_amount(
                                                myex.get_sell1_price()))
        except ZeroDivisionError:
            max_buy_amount_mesg = 'N/A'
        row = [
            myex.name,
            '%.1f' % myex.delay,

            '%.*f' % (price_prec, myex.get_buy1_price()),
            '%.*f' % (price_prec, myex.get_sell1_price()),
            '%.*f' % (price_prec, myex.get_last_price()),

            '%.*f' % (amount_prec, myex.account['Stocks']),
            '%.*f' % (amount_prec, myex.account['FrozenStocks']),
            '%.*f' % (price_prec, myex.account['Balance']),
            '%.*f' % (price_prec, myex.account['FrozenBalance']),

            max_buy_amount_mesg,
            '%7.2f' % myex.get_position_offset(),
        ]
        assert len(table_exchange_dynamic['cols']) == len(row)
        table_exchange_dynamic['rows'].append(row)

    table_exchange_static = {
        'type': 'table',
        'title': '交易所静态信息',
        # headers
        'cols': [
            '交易所',
            'API模式',
            '轮询倍率',
            '价格精度',
            '数量精度',
            '买单手续费(%)',
            '卖单手续费(%)',
            '手续费模式',
        ],
        'rows': [],
    }

    for myex in myex_list:
        row = [
            myex.name,
            myex.api_mode,
            myex.inter_times,
            myex.price_prec,
            myex.amount_prec,
            '%.2f' % myex.trdfee['Buy'],
            '%.2f' % myex.trdfee['Sell'],
            myex.fees_mode,
        ]
        assert len(table_exchange_static['cols']) == len(row)
        table_exchange_static['rows'].append(row)

    table_exchange_arbit_stats = {
        'type': 'table',
        'title': '交易所套利信息',
        'rows': [],
        'cols': [
            '交易所',

            '套利买单数',
            '套利买单量(%s)' % base,
            '被取消数',
            '被取消量(%s)' % base,

            '套利卖单数',
            '套利卖单量(%s)' % base,
            '被取消数',
            '被取消量(%s)' % base,
        ]
    }

    for myex in myex_list:
        row = [
            myex.name,

            myex.get_stats('order', 'arbit', 'buy', 'count'),
            '%.*f' % (amount_prec, myex.get_stats('order', 'arbit', 'buy', 'amount')),
            myex.get_stats('cancel', 'arbit', 'buy', 'count'),
            '%.*f' % (amount_prec, myex.get_stats('cancel', 'arbit', 'buy', 'amount')),

            myex.get_stats('order', 'arbit', 'sell', 'count'),
            '%.*f' % (amount_prec, myex.get_stats('order', 'arbit', 'sell', 'amount')),
            myex.get_stats('cancel', 'arbit', 'sell', 'count'),
            '%.*f' % (amount_prec, myex.get_stats('cancel', 'arbit', 'sell', 'amount')),
        ]
        assert len(table_exchange_arbit_stats['cols']) == len(row)
        table_exchange_arbit_stats['rows'].append(row)

    li = []
    for a in ('order', 'cancel'):
        #for b in ('close_force', 'close_retry_arbit', 'close_arbit_reverse', 'close_retry_arbit_reverse'):
        #for b in ('close_force', 'close_retry_arbit', 'close_arbit_reverse'):
        for b in ('close_force', 'close_retry_arbit'):
            for c in ('buy', 'sell'):
                for d in ('amount', 'count'):
                    li.append('.'.join([a, b, c, d]))
    li.append('.'.join(['cancel', 'unknown', 'buy', 'amount']))
    li.append('.'.join(['cancel', 'unknown', 'buy', 'count']))
    li.append('.'.join(['cancel', 'unknown', 'sell', 'amount']))
    li.append('.'.join(['cancel', 'unknown', 'sell', 'count']))
    li.append('cancel.arbit.profit')

    table_exchange_stats = {
        'type': 'table',
        'title': '交易所统计信息',
        'rows': [],
        'cols': [],
    }

    table_exchange_stats['cols'].append('Statistics')
    for myex in myex_list:
        table_exchange_stats['cols'].append(myex.name)

    for key in li:
        row = [key]
        for myex in myex_list:
            row.append(myex.stats.get(key, 0.0))
        assert len(table_exchange_stats['cols']) == len(row)
        table_exchange_stats['rows'].append(row)

    tables.append(table_baseinfo)
    tables.append(table_summary)
    tables.append([table_exchange_dynamic, table_exchange_static])
    if is_run_on_botvs():
        if is_debug_mode():
            tables.append([table_exchange_arbit_stats, table_exchange_stats])
        else:
            tables.append(table_exchange_arbit_stats)
    elif is_baktest_mode():
        tables.append([table_exchange_arbit_stats, table_exchange_stats])
    else:
        tables.append(table_exchange_arbit_stats)
    _draw_table(*tables)

# 交易所间的套利统计信息
r'''
g_arbit_stats = {
    'Binance:' {
        'OKEX': {
            # 下单成功的时候添加统计，取消的时候不减，只加取消的统计
            # 因为 a - b = c, 只保存 a 和 b 即可获取全部信息，无需特意保存 c
            'executed': {
                'buy': {
                    'amount': 0.0,
                    'volume': 0.0,
                },
                'sell': {
                    'amount': 0.0,
                    'volume': 0.0,
                },
                # 只计算确认撮合了的交易对产生的利润, 亏损的话就是负数
                # stats 不管，status 才计算
                'profit': {
                    'amount': 0.0,
                    'volume': 0.0,
                },
            },

            # 被取消的或者下单失败的
            'canceled': {
                'buy': {
                    'amount': x,
                    'volume': y,
                },
                'sell': {
                    'amount': x,
                    'volume': y,
                },
                # 直接根据 sell 和 buy 的 volume 的等 amount 差价算出的利润，非实际利润
                'profit': {
                    'amount': x,
                    'volume': y,
                }
            },
        },
        ...
    },
    ...
}
'''
# NOTE: 为了自己撮合的时候，更简单的处理，这两个字典的 amount 都是不包括手续费的
#       只需要在执行下单买卖的时候增加买量，统计的时候减少买量即可
g_arbit_stats = {}
g_arbit_status = {} # 和 stats 的区别是，status 会裁剪
def init_arbit_stats(myex_list):
    global g_arbit_stats
    global g_arbit_status
    for a in myex_list:
        for b in myex_list:
            if a is b:
                continue
            d = {
                'executed': {
                    'sell': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                    'buy': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                    'profit': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                },
                'canceled': {
                    'sell': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                    'buy': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                    'profit': {
                        'amount': 0.0,
                        'volume': 0.0,
                    },
                },
            }
            a_name = a.name
            b_name = b.name
            g_arbit_stats[a_name] = g_arbit_stats.setdefault(a_name, {})
            g_arbit_stats[a_name][b_name] = d

    g_arbit_status = copy.deepcopy(g_arbit_stats)

def _trim_arbit_status(di, sell_fee, buy_fee):
    sell_amount = di['sell']['amount']
    buy_amount = di['buy']['amount']
    pub_amount = min(sell_amount, buy_amount)
    if not pub_amount:
        return
    sell_fee_ratio = sell_fee / 100.0
    buy_fee_ratio = buy_fee / 100.0
    sell_volume = di['sell']['volume']
    buy_volume = di['buy']['volume']
    sell_vwap = sell_volume / sell_amount
    buy_vwap = buy_volume / buy_amount
    profit = (sell_vwap - buy_vwap
              - sell_vwap * sell_fee_ratio
              - buy_vwap * buy_fee_ratio) * pub_amount
    di['profit']['amount'] += pub_amount
    di['profit']['volume'] += profit
    di['sell']['amount'] -= pub_amount
    di['buy']['amount'] -= pub_amount
    di['sell']['volume'] -= sell_vwap * pub_amount
    di['buy']['volume'] -= buy_vwap * pub_amount

def get_myex_by_name(name, myex_list=None):
    global g_myex_list
    # MyExchange('binance')
    name = name[12:-2] if name.startswith("MyExchange('") else name
    myex_list = g_myex_list if myex_list is None else myex_list
    for myex in myex_list:
        if name == myex.name:
            return myex
    return None

def reset_all_canceled_status(myex_list):
    for myex in myex_list:
        reset_canceled_status(myex_list, myex)

def reset_canceled_status(myex_list, myex):
    '''
    重置指定myex的所有取消的订单的信息
    '''
    global g_arbit_status
    for myex_b in myex_list:
        myex_a = myex
        if myex_a is myex_b:
            continue
        dic = g_arbit_status[myex_a.name][myex_b.name]['canceled']['sell']
        dic['amount'] = 0.0
        dic['volume'] = 0.0
    for myex_a in myex_list:
        myex_b = myex
        if myex_a is myex_b:
            continue
        dic = g_arbit_status[myex_a.name][myex_b.name]['canceled']['buy']
        dic['amount'] = 0.0
        dic['volume'] = 0.0

def trim_all_arbit_status(myex_list):
    '''计算所有的状态，把已经成对的交易清理并结算成收益(profit)'''
    global g_arbit_status
    for myex_a in myex_list:
        di = g_arbit_status[myex_a.name]
        for b_name in di.keys():
            status = di[b_name]
            myex_b = get_myex_by_name(b_name, myex_list)
            _trim_arbit_status(status['executed'],
                               myex_a.trdfee['Sell'], myex_b.trdfee['Buy'])
            _trim_arbit_status(status['canceled'],
                               myex_a.trdfee['Sell'], myex_b.trdfee['Buy'])

def update_arbit_sell_stats(a_name, b_name, key, sell_price, amount, sub=False):
    global g_arbit_stats
    global g_arbit_status
    d = g_arbit_stats[a_name][b_name][key]
    status = g_arbit_status[a_name][b_name][key]
    if sub:
        d['sell']['amount'] -= amount
        d['sell']['volume'] -= sell_price * amount
        status['sell']['amount'] -= amount
        status['sell']['volume'] -= sell_price * amount
    else:
        d['sell']['amount'] += amount
        d['sell']['volume'] += sell_price * amount
        status['sell']['amount'] += amount
        status['sell']['volume'] += sell_price * amount

def update_arbit_buy_stats(a_name, b_name, key, buy_price, amount, sub=False):
    '''
    amount 必须为下单原始 amount，这个函数负责修正为无手续费的 amount
    '''
    global g_arbit_stats
    global g_arbit_status
    d = g_arbit_stats[a_name][b_name][key]
    status = g_arbit_status[a_name][b_name][key]

    bak_amount = amount
    #myex_a = get_myex_by_name(a_name)
    myex_b = get_myex_by_name(b_name)
    if myex_b.fees_mode == myex_b.FEES_MODE_FORWARD:
        # 买单的交易所的话，如果手续费为前向模式，那么到手的 amount 要扣手续费的
        amount *= (1.0 - myex_b.buy_fee_ratio)

    if sub:
        d['buy']['amount'] -= amount
        d['buy']['volume'] -= buy_price * amount
        status['buy']['amount'] -= amount
        status['buy']['volume'] -= buy_price * amount
    else:
        d['buy']['amount'] += amount
        d['buy']['volume'] += buy_price * amount
        status['buy']['amount'] += amount
        status['buy']['volume'] += buy_price * amount

# 所有交易所间的 ticker 状态信息
r'''
g_alltk_status = {
    'Binance': {
        # 最后成交价的差价
        'last_diff': {
            'OKEX': {
                # 以下三项正负对称
                'last': {
                    'value': 1.1, # 最近的差价 Binance.Last - OKEX.Last
                    'timestamp': 1516876917.305309 # time.time() 最近更新的时间戳
                },
                'avrg': {
                    'value': 1.0, # 至此的平均价
                    'timestamp': 1516876917.305309
                    'times': 1,
                },
                'tune': {
                    'value': 0.9, # 策略微调用的差价，即原版的 delta
                    'timestamp': 1516876917.305309
                },
                # 微调信息
                'tune_info': {
                    'diffs': 3.3,   # 暂时用这个方法微调, 每次累计
                    'times': 3,
                    'timestamp': 1516876917.305309
                }
            },
        },
        # 买1 卖1 差价，根据现时的观察，平均值比较好用
        'b1s1_diff': {
            'OKEX': {
                # 以下三项不对称
                'last': {
                    'value': 1.1, 
                    'timestamp': 1516876917.305309
                },
                'avrg': {
                    'value': 1.1, 
                    'timestamp': 1516876917.305309
                    'times': 1,
                },
                'tune': {
                    'value': 1.1, 
                    'timestamp': 1516876917.305309,
                },
                # 微调信息
                'tune_info': {
                    'diffs': 3.3,   # 暂时用这个方法微调, 每次累计
                    'times': 3,
                    'timestamp': 1516876917.305309
                }
            }
        },
    },
    ...
} 
'''
g_alltk_status = {}
def init_alltk_status(myex_list):
    '''
    根据最初的 ticker 信息更新 g_alltk_status 的信息

    binance
    {
        "Buy": 0.003509,
        "Last": 0.003508,
        "Sell": 0.003522
    }
    huobipro
    {
        "Buy": 0.003502,
        "Last": 0.003517,
        "Sell": 0.003517
    }
    okex
    {
        "Buy": 0.00348497,
        "Last": 0.00350339,
        "Sell": 0.00353115
    }

    binance - huobipro
    last_diff    	-0.000009
    b1s1_diff	-0.000008
    b1s1_diff_r	-0.00002

    binance - okex
    last_diff	0.00000461
    b1s1_diff	-0.00002215
    b1s1_diff_r	-0.00003703

    huobipro - okex
    last_diff	0.00001361
    b1s1_diff	-0.00002915
    b1s1_diff_r	-0.00003203
    '''
    global g_alltk_status
    ts = time.time()
    for a in myex_list:
        for b in myex_list:
            if a is b:
                continue
            # 开始更新
            a_name = a.name
            b_name = b.name
            a_last_diff = a.ticker['Last'] - b.ticker['Last']
            a_b1s1_diff = a.ticker['Buy'] - b.ticker['Sell']

            # 初始化的时候, 都使用第一个值
            for k in ('last', 'avrg', 'tune'):
                set_alltk_status(a_name, 'last_diff', b_name, k, 'value', v=a_last_diff)
                set_alltk_status(a_name, 'last_diff', b_name, k, 'timestamp', v=ts)
                if k == 'avrg':
                    set_alltk_status(a_name, 'last_diff', b_name, k, 'times', v=1)

            set_alltk_status(a_name, 'last_diff', b_name, 'tune_info', 'diffs', v=a_last_diff)
            set_alltk_status(a_name, 'last_diff', b_name, 'tune_info', 'times', v=1)
            set_alltk_status(a_name, 'last_diff', b_name, 'tune_info', 'timestamp', v=ts)

            # 初始化的时候, 都使用第一个值
            for k in ('last', 'avrg', 'tune'):
                set_alltk_status(a_name, 'b1s1_diff', b_name, k, 'value', v=a_b1s1_diff)
                set_alltk_status(a_name, 'b1s1_diff', b_name, k, 'timestamp', v=ts)
                if k == 'avrg':
                    set_alltk_status(a_name, 'b1s1_diff', b_name, k, 'times', v=1)

            set_alltk_status(a_name, 'b1s1_diff', b_name, 'tune_info', 'diffs', v=a_b1s1_diff)
            set_alltk_status(a_name, 'b1s1_diff', b_name, 'tune_info', 'times', v=1)
            set_alltk_status(a_name, 'b1s1_diff', b_name, 'tune_info', 'timestamp', v=ts)

            # @ 需要进一步对初始的 last_diff 进行修正
            max_diff = abs(get_param('G_PARAM_MAX_DIFF'))
            # 开始的时候对差价的接受程度
            delta_param = get_param('G_PARAM_DELTA_PARAM')
            if abs(a_last_diff) < max_diff * 0.3:   # 需要缩小
                delta_xx = 0.2 * delta_param
            elif abs(a_last_diff) < max_diff * 0.7: # 需要缩小
                delta_xx = 0.5 * delta_param
            else:
                delta_xx = delta_param
            init_last_diff = a_last_diff * delta_xx / 100.0
            set_alltk_status(a_name, 'last_diff', b_name, 'tune', 'value', v=init_last_diff)
            #set_alltk_status(a_name, 'last_diff', b_name, 'tune_info', 'diffs', v=0.0)
            #set_alltk_status(a_name, 'last_diff', b_name, 'tune_info', 'times', v=0)

def _update_alltk_status(a_name, a_ticker, b_name, b_ticker, ts=None):
    '''根据提供的最新的 ticker 更新数据, 单向更新'''
    global g_alltk_status
    a_last_diff = a_ticker['Last'] - b_ticker['Last']
    a_b1s1_diff = a_ticker['Buy'] - b_ticker['Sell']

    if isinstance(a_name, MyExchange):
        a_name = a_name.name
    if isinstance(b_name, MyExchange):
        b_name = b_name.name

    ts = ts if not ts is None else time.time()
    # 更新 last_diff/b1s1_diff - last
    set_alltk_status(a_name, 'last_diff', b_name, 'last', 'value', v=a_last_diff)
    set_alltk_status(a_name, 'last_diff', b_name, 'last', 'timestamp', v=ts)
    set_alltk_status(a_name, 'b1s1_diff', b_name, 'last', 'value', v=a_b1s1_diff)
    set_alltk_status(a_name, 'b1s1_diff', b_name, 'last', 'timestamp', v=ts)

    # 更新 last_diff/b1s1_diff - avrg
    value = get_alltk_status(a_name, 'last_diff', b_name, 'avrg', 'value')
    times = get_alltk_status(a_name, 'last_diff', b_name, 'avrg', 'times')
    newval = (value * times + a_last_diff) / float(times + 1)
    set_alltk_status(a_name, 'last_diff', b_name, 'avrg', 'value', v=newval)
    set_alltk_status(a_name, 'last_diff', b_name, 'avrg', 'timestamp', v=ts)
    set_alltk_status(a_name, 'last_diff', b_name, 'avrg', 'times', v=(times+1))

    value = get_alltk_status(a_name, 'b1s1_diff', b_name, 'avrg', 'value')
    times = get_alltk_status(a_name, 'b1s1_diff', b_name, 'avrg', 'times')
    newval = (value * times + a_b1s1_diff) / float(times + 1)
    set_alltk_status(a_name, 'b1s1_diff', b_name, 'avrg', 'value', v=newval)
    set_alltk_status(a_name, 'b1s1_diff', b_name, 'avrg', 'timestamp', v=ts)
    set_alltk_status(a_name, 'b1s1_diff', b_name, 'avrg', 'times', v=(times+1))

    # 更新 last_diff/b1s1_diff - tune_info
    g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['diffs'] += a_last_diff
    g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['times'] += 1
    g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['timestamp'] = ts
    g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['diffs'] += a_b1s1_diff
    g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['times'] += 1
    g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['timestamp'] = ts

    learn_speed = get_param('G_PARAM_LEARN_SPEED')
    # 微调阈值, 暂时为 20
    if g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['times'] >= 20:
        diff_avg = g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['diffs'] / 20.0
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
        newtune = get_alltk_status(a_name, 'last_diff', b_name,
                                   'tune', 'value') * p0 + diff_avg * p1
        set_alltk_status(a_name, 'last_diff', b_name, 'tune', 'value', v=newtune)
        set_alltk_status(a_name, 'last_diff', b_name, 'tune', 'timestamp', v=ts)
        g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['diffs'] = 0.0
        g_alltk_status[a_name]['last_diff'][b_name]['tune_info']['times'] = 0

    # 微调阈值, 暂时为 20
    if g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['times'] >= 20:
        diff_avg = g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['diffs'] / 20.0
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
        newtune = get_alltk_status(a_name, 'b1s1_diff', b_name,
                                   'tune', 'value') * p0 + diff_avg * p1
        set_alltk_status(a_name, 'b1s1_diff', b_name, 'tune', 'value', v=newtune)
        set_alltk_status(a_name, 'b1s1_diff', b_name, 'tune', 'timestamp', v=ts)
        g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['diffs'] = 0.0
        g_alltk_status[a_name]['b1s1_diff'][b_name]['tune_info']['times'] = 0


def update_alltk_status(a_name, a_ticker, b_name, b_ticker):
    '''双向更新'''
    ts = time.time()
    _update_alltk_status(a_name, a_ticker, b_name, b_ticker, ts=ts)
    _update_alltk_status(b_name, b_ticker, a_name, a_ticker, ts=ts)

def set_alltk_status(*keys, **kwargs):
    global g_alltk_status
    assert 'v' in kwargs
    d = g_alltk_status
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = kwargs.get('v')

def get_alltk_status(*keys, **kwargs):
    '''
    Binance.last_diff.OKEX.last.value
    '''
    global g_alltk_status
    d = g_alltk_status
    try:
        for k in keys:
            d = d[k]
    except KeyError:
        return kwargs.get('default')
    return d

def _dump_info(myex_list):
    print('g_arbit_stats = \n' + json.dumps(g_arbit_stats, indent=4, sort_keys=True))
    print('g_alltk_status = \n' + json.dumps(g_alltk_status, indent=4, sort_keys=True))
    for myex in myex_list:
        print('[%s] stats = \n' % myex.name + json.dumps(myex.stats, indent=4, sort_keys=True))

def seconds_to_loop_count(seconds, loop_interval_ms):
    if loop_interval_ms == 0.0:
        return 1
    i = int(seconds * 1000.0 / loop_interval_ms)
    i = 1 if i < 1 else i
    return i

_g_global_save_vars = [
    'g_version_info',
    'g_all_init_fund',
    'g_arbit_stats',
    'g_arbit_status',
    'g_stats',
]
# 无需从存档来初始化的变量
_g_exclude_global_save_vars = {
    'birth_time',
    'version_info',
    'g_version_info',
    'myex_list',
}
_g_myex_attrs = [
    'name',
    'currency',
    'executed_orders',
    'stats',
    'pending_force',
    'base_stocks',
]
def make_save_data(myex_list, birth_time=None):
    global g_save_birth_time
    data = {}
    for k in _g_global_save_vars:
        data[k] = eval(k)
    data['myex_list'] = []
    for myex in myex_list:
        d = {}
        for prop in _g_myex_attrs:
            d[prop] = getattr(myex, prop)
            if prop == 'executed_orders':
                d[prop] = norm4json(d[prop])
        data['myex_list'].append(d)

    if birth_time:
        if isinstance(birth_time, bool):
            birth_time = get_strtime()
        g_save_birth_time = birth_time
    data['birth_time'] = g_save_birth_time

    # 存档的版本
    data['version_info'] = [1, 0, 0]

    return data

def save_data_to_file(myex_list, birth_time=None, fname=None):
    '''
    包括的内容
        - birth_time (存档创建的时间，写同一个存档的时候，不更新此值)
        - g_version_info
        - g_all_init_fund
        - g_arbit_stats
        - g_arbit_status
        - g_stats
        - myex_list
            * name
            * currency
            * executed_orders
            * stats
            * pending_force
    '''
    if is_baktest_mode() and get_loop_count() > 1 and get_loop_count() % 3600 != 0:
        return

    data = make_save_data(myex_list, birth_time)
    fname = get_param('G_PARAM_SAVE_FILE_NAME') if fname is None else fname
    try:
        with open(fname, 'w') as f:
            f.write(encrypt_data(json.dumps(data)))
    except:
        Log('存档保存失败！')
        Log(traceback.format_exc())

    try:
        with open(fname + '.bak', 'w') as f:
            f.write(encrypt_data(json.dumps(data)))
    except:
        Log('存档备份保存失败！')
        Log(traceback.format_exc())

def _load_json_from_file(fname):
    try:
        with open(fname, 'r') as f:
            data = json.loads(decrypt_data(f.read()))
    except:
        Log('读取存档失败，尝试从备份存档中读取...')
        LogDebug(traceback.format_exc())
        try:
            with open(fname + '.bak', 'r') as f:
                data = json.loads(decrypt_data(f.read()))
        except:
            Log('读取备份存档失败')
            LogDebug(traceback.format_exc())
            raise Exception('Panic!')
    Log('读取存档成功。')
    return unicode2str(data)

def load_data_from_file(myex_list, fname=None):
    global g_save_birth_time
    fname = get_param('G_PARAM_SAVE_FILE_NAME') if fname is None else fname
    data = _load_json_from_file(fname)
    for k, v in data.items():
        if k in _g_exclude_global_save_vars:
            if k == 'birth_time':
                g_save_birth_time = v
            continue
        var = eval(k)
        if isinstance(var, dict):
            var.update(v)
        else:
            # 我们不支持非字典类型的全局变量从存档初始化
            Log('内部错误：存档全局变量类型错误')
            assert False

    myex_set = set([e.name for e in myex_list])
    for myex in myex_list:
        for i in data['myex_list']:
            if not i['name'] in myex_set:
                Log('当前设置的交易所不包括存档中的交易所 %s，无法使用存档。' % i['name'])
                raise Exception('Panic')
            if i['currency'] != myex.currency:
                Log('当前设置的交易对不包括存档中的交易对 %s，无法使用存档。' % i['currency'])
                raise Exception('Panic')
            if i['name'] != myex.name:
                continue
            for attr in _g_myex_attrs:
                setattr(myex, attr, i[attr])
            for oid, order in myex.executed_orders.items():
                if 'pair_info' in order:
                    pi = order['pair_info']
                    pi['sell_myex'] = get_myex_by_name(pi['sell_myex'])
                    pi['buy_myex'] = get_myex_by_name(pi['buy_myex'])

def encrypt_data(data):
    '''data为字符串'''
    global g_logfname
    logfname = g_logfname[:8]
    a = sorted(logfname)
    b = sorted(logfname, reverse=True)
    data += '\0' * (16 - len(data) % 16)
    obj = AES.new(''.join(a+b).encode(), AES.MODE_CBC, ''.join(b+a).encode())
    return base64.b64encode(obj.encrypt(data.encode())).decode()

def decrypt_data(data):
    '''data为字符串'''
    global g_logfname
    logfname = g_logfname[:8]
    a = sorted(logfname)
    b = sorted(logfname, reverse=True)
    obj = AES.new(''.join(a+b).encode(), AES.MODE_CBC, ''.join(b+a).encode())
    return obj.decrypt(base64.b64decode(data.encode())).decode().rstrip('\0')

def signal_handler(signum, frame):
    global g_running
    LogDebug('Signal handler called with signal', signum)
    g_running = False
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
### 主要流程
#       - 取消未完成订单
#       - 平仓
#       - 套利
#
#
# 只有两大类交易
#       - 套利交易
#       - 平仓交易 (目前仅实现 2 种)
#           - 重试套利平仓
#           - 强制平仓
#           X 反套利平仓
#           X 重试反套利平仓
#
# 只有两个函数处理交易
#       - process_arbitrage_trade   - 处理套利交易对
#       - process_close_orders      - 处理平仓交易
#
# 流程优化，这样的流程可以保证账号信息不冲突，还有保证均衡的刷新间隔
# 每一轮只执行一种有效的工作 - (清理订单, 套利, 平仓) 三选一
# 这样有利于实现逻辑清晰:
#       - 取消冻结订单
#       - 刷新数据
#       - 平仓交易
#       - 套利交易
#
# 理解以下的含义和作用
#   - delta
#   - beta_rock
#   - taoli_cha
#
# 亏损唯一来源: 套利订单未成交  (1)
# 套利终止原因: 只能单向套利    (2)
# 处理方法:
#   (1) 重试套利交易
#   (2) 反向套利平仓
#
# 额外处理(强制平仓大几率造成亏损, 最大程度避免强制平仓):
#   - 强制平仓 (各种复杂情况下造成仓位偏移时)
def mainloop(all_init_fund, myex_list):
    global g_running
    global g_loop_count
    # 循环间隔，单位毫秒
    loop_interval = get_param('G_PARAM_LOOP_INTERVAL')
    # 增强学习次数
    boost_learn_count = get_param('G_PARAM_BOOST_LEARN_COUNT')
    # 是否使用存档
    use_save = bool(get_param('G_PARAM_SAVE_FILE_NAME'))
    # 是否从存档初始化
    init_from_save = use_save and get_param('G_PARAM_INIT_FROM_SAVE') and \
                     os.path.exists(get_param('G_PARAM_SAVE_FILE_NAME'))
    # 是否自动取消冻结订单
    enable_cancel_orders = get_param('G_PARAM_ENABLE_CANCEL_ORDERS')

    myex_comp_list = generate_compare_list(myex_list)

    # TODO
    # 最近的套利交易数量，套利差更新后会重置
    last_trade_amount = 0.0
    # 这个用来更新套利差的，每次循环加 1，套利差更新后重置
    tune_arbit_diff_threshold = 0

    # @ hack for test
    #for myex in myex_list:
    #    myex.botvs_exchange._set_account(Balance=0.0, Stocks=40.0)
    #    myex.account_refresh_state = 'refresh_instant'

    LogProfit_interval = seconds_to_loop_count(1800, loop_interval)
    save_interval = seconds_to_loop_count(1, loop_interval)

    if get_param('G_PARAM_RESET_PROFIT_LOG'):
        LogProfitReset()

    # 这样可以保证第一次进入循环不睡眠
    prev_loop_time = 0.0
    while g_running:
        g_loop_count += 1
        loop_count = g_loop_count
        tune_arbit_diff_threshold += 1

        # 本轮是否已经工作了? 取消未完成订单, 套利, 平仓都称为工作
        worked = False

        # @ 保持每次循环持续时间为 loop_interval，如果循环时间过长，不睡眠
        curr_loop_time = time.time()
        loop_time_diff_ms = (curr_loop_time - prev_loop_time) * 1000.0
        if loop_time_diff_ms < loop_interval:
            if not is_baktest_mode():
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
        if is_baktest_mode() and loop_count > 1:
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
                _dump_info(myex_list)
                break

        # @ 取消未完成的订单, 取消订单不需要最新的 account, ticker, depth
        if enable_cancel_orders and loop_count % 90 == 0:
            cancel_incompl_orders(myex_list)
            if get_last_cancel_order_timestamp() == loop_count:
                worked = True

        # @ 刷新交易所数据
        clean_exchange_data(myex_list, loop_count)  # 暂时只清理深度和延时数据
        # 获取 account, ticker, depth
        fetch_exchange_data(myex_list, myex_comp_list, loop_count)

        # @ 更新 alltk_status
        for (myex_a, myex_b) in myex_comp_list:
            if myex_a.ticker_tick == loop_count and \
               myex_b.ticker_tick == loop_count and loop_count > 1:
                # NOTE: 只有是最新的ticker的时候才更新 (这样做对不对?)
                update_alltk_status(myex_a.name, myex_a.ticker,
                                    myex_b.name, myex_b.ticker)

        # @ 更新套利差
        # 阈值是魔数...
        if tune_arbit_diff_threshold > 288 * len(myex_list):
            if tune_arbit_diff(last_trade_amount):
                tune_arbit_diff_threshold = 0
                last_trade_amount = 0.0

        # @ 处理 g_arbit_status, 这是平仓的重要依据
        trim_all_arbit_status(myex_list)

        # @ 策略平仓
        if not worked:
            if close_the_position(myex_list):
                worked = True

        # @ 进行套利
        if loop_count < boost_learn_count:
            if loop_count == 1 or loop_count % 100 == 0:
                Log('当前第 %d 次观察大盘，再观察 %d 次后开始交易。'
                    % (loop_count, boost_learn_count - loop_count))
        elif loop_count == boost_learn_count:
            Log(('已经观察大盘 %d 次，如果监测到有套利机会，将开始交易。' +
                 '当前轮询次数为：%d') % (boost_learn_count, loop_count))
        else: # (> boost_learn_count) *** 执行策略 ***
            if loop_count % 3600 == 0 or loop_count == 1:
                Log('正在观察大盘，如果监测到有套利机会，'
                    + '将开始交易。当前轮询次数为：%d' % loop_count)
            all_trade_list = []
            # 在模拟测试模式，得到套利机会后要等待若干回合，
            # 否则可能反复打印同样的套利交易
            if (is_baktest_mode() or is_emulate_mode()) and \
               loop_count < (get_last_arbitrage_timestamp() + 1 +
                             get_param('G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE')):
                pass
            # 只有在本轮没有执行过重试交易和趋势平仓交易时，才尝试套利
            elif not worked:
                if loop_count >= (get_last_arbitrage_timestamp() +
                                  get_param('G_PARAM_PAUSE_ROUND_AFTER_TRADE')):
                    all_trade_list = make_arbit_trades(myex_comp_list)
            # 处理这些可能套利的订单
            ret = process_arbitrage_trades(myex_list, all_trade_list)
            last_trade_amount += ret
            if ret:
                worked = True
                LogDebug('策略计算所得套利订单为：%s'
                         % json.dumps(norm4json(all_trade_list),
                                      indent=None, sort_keys=True))

        # @ 刷新状态信息
        op_delay_ms = (time.time() - prev_loop_time) * 1000.0
        all_curr_fund = get_all_fund(myex_list)
        if is_baktest_mode():
            if loop_count % 3600 == 0:
                refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms)
        else:
            refresh_status(myex_list, all_curr_fund, all_init_fund, op_delay_ms)

        if (loop_count - 1) % LogProfit_interval == 0:
            LogProfit(calc_real_arbit(all_init_fund, all_curr_fund))

        if use_save and (loop_count - 1) % save_interval == 0:
            birth_time = loop_count == 1 and not init_from_save
            save_data_to_file(myex_list, birth_time)

def currency_to_base_quote(currency):
    '''
    BTC_USDT -> BTC, USDT
    '''
    li = currency.split('_')
    if (len(li) >= 2):
        return li[0], li[1]
    else:
        return li[0], ''

def check_strategy_params():
    # 检查参数合法性
    assert get_param('G_PARAM_LOOP_INTERVAL') > 0
    assert isinstance(get_param('G_PARAM_LOOP_INTERVAL'), int)

    assert get_param('G_PARAM_EMU_BALANCE') > 0.0
    assert get_param('G_PARAM_EMU_STOCKS') > 0.0
    assert get_param('G_PARAM_EMU_PAUSE_ROUND_AFTER_TRADE') >= 0
    assert get_param('G_PARAM_WAIT_FOR_ORDER') >= 0
    assert get_param('G_PARAM_FORCE_CLOSE_OFFSET_THRESHOLD') > 10.0

    assert get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN') >= 0.0
    assert get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN') <= \
           get_param('G_PARAM_ARBITRAGE_DIFFERENCE')
    assert get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MAX') >= \
           get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MIN')
    assert get_param('G_PARAM_ARBITRAGE_DIFFERENCE_MAX') < 100.0

    assert get_param('G_PARAM_BASE_TRADE_AMOUNT') > 0.0
    assert get_param('G_PARAM_MIN_TRADE_AMOUNT') > 0.0
    assert get_param('G_PARAM_BOOST_LEARN_COUNT') >= 0
    assert get_param('G_PARAM_SLIP_POINT') >= 0.0
    assert get_param('G_PARAM_MAX_DIFF') >= 0.0

    assert get_param('G_PARAM_PRICE_PREC') >= 0
    assert isinstance(get_param('G_PARAM_PRICE_PREC'), int)

    assert get_param('G_PARAM_AMOUNT_PREC') >= 0
    assert isinstance(get_param('G_PARAM_AMOUNT_PREC'), int)

    if get_param('G_PARAM_CUSTOM_INIT_FUND'):
        assert get_param('G_PARAM_CUSTOM_INIT_STOCKS') > 0.0 or \
               get_param('G_PARAM_CUSTOM_INIT_BALANCE') > 0.0

def process_param_interval_times(myex_list):
    li = get_param('G_PARAM_EXCHANGE_INTERVAL_TIMES').strip().split(',')
    li = [e.strip() for e in li]
    li += ['1'] * len(myex_list)

    for idx, myex in enumerate(myex_list):
        inter_times = li[idx]
        if inter_times == '':
            continue
        try:
            inter_times = int(inter_times)
            if inter_times <= 0:
                inter_times = 1
        except:
            return False
        myex.inter_times = inter_times

    return True

def process_param_base_stocks(myex_list):
    base_stocks = get_param('G_PARAM_EXCHANGE_BASE_STOCKS')
    li = base_stocks.strip().split(',')
    li = [e.strip() for e in li]
    li += [None] * len(myex_list)
    for idx, myex in enumerate(myex_list):
        base_stocks = li[idx]
        if base_stocks is None or base_stocks == '':
            continue

        try:
            base_stocks = float(base_stocks)
        except:
            return False
        if base_stocks < 0.0:
            return False
        myex.base_stocks = base_stocks
    return True

def process_param_enabled_flags(myex_list):
    li = get_param('G_PARAM_ENABLED_FLAGS').split(',')
    li = [e.strip() for e in li]
    li += ['1'] * len(myex_list)
    for idx, myex in enumerate(myex_list):
        flag = li[idx]
        if flag == '':
            continue
        try:
            myex.enabled = bool(int(flag))
        except:
            return False
    return True

def process_param_trade_fees_modes(myex_list):
    li = get_param('G_PARAM_TRADE_FEES_MODES').split(',')
    li = [e.strip() for e in li]
    li += ['0'] * len(myex_list)
    for idx, myex in enumerate(myex_list):
        fees_mode = li[idx]
        if fees_mode == '':
            continue
        try:
            fees_mode = int(fees_mode)
            if fees_mode < MyExchange.FEES_MODE_FORWARD or \
               fees_mode > MyExchange.FEES_MODE_BALANCE:
                return False
            myex.fees_mode = fees_mode
        except:
            return False
    return True

def process_param_custom_init_fund(all_init_fund):
    all_init_fund['stocks'] = get_param('G_PARAM_CUSTOM_INIT_STOCKS')
    all_init_fund['balance'] = get_param('G_PARAM_CUSTOM_INIT_BALANCE')
    all_init_fund['total'] = all_init_fund['balance'] + all_init_fund['stocks'] * all_init_fund['price']
    all_init_fund['Balance'] = all_init_fund['balance']
    all_init_fund['FrozenBalance'] = 0.0
    all_init_fund['Stocks'] = all_init_fund['stocks']
    all_init_fund['FrozenStocks'] = 0.0

def init_logfname(exchanges):
    global g_logfname
    logfname = os.path.splitext(g_logfname)[0]
    # symarbit-[Binance(QTUM_BTC),OKEX(QTUM_BTC)].log
    li = []
    for ex in exchanges:
        li.append('%s(%s)' % (bytes2str(ex.GetName()), bytes2str(ex.GetCurrency())))
    logfname += '-[' + ','.join(li) + '].log'
    g_logfname = logfname

def __verify_key(key):
    import rsa
    from rsa import PublicKey, PrivateKey
    b64prik = b'UHJpdmF0ZUtleSg5OTM0MzE2OTQzODM4MzkxMDk2NjY2MDU1NzAxMzcyMzMyMDU0NTIyNTMyODA3NzM0OTEwNzM4MzQyMjkxNzIxNDk0NDUzOTA2NzgwOTE5MjIxNzM3MjI1NDU1MzA4MzUwODMyNzIyOTQ4MDMyNzU2OTQ5MzAzMzE5NjgwNzEzMDU0MDE4NTI0OTQ3NjE4NzMxMjI3NjAxMzMxLCA2NTUzNywgNjk0NTI0NTE4NTY2Mjg2ODM1MzI1MTUyNzIzMDgwODIwNzczMTExNTQ1MjQ2NDc4NzgwMTM5NzgyNjY3OTkyMjcyMjAxNzkyNTY3NTUyNDM2NzcxMDE0MDM1NTA5MjkxMjAwNTAxMDUyNTMyOTI4OTk2NzQ1NDI5NTI4MDg0NjA2OTI1NjcxNjYzMjA4ODE5MDU1NzE4ODcyMSwgNjY3NjIyNTg1NzY3MDc2MDUzMzQ2MTQ1Mzg5MzU1MzY2NzQzMjY5NjU2MTAxMDY4NjEwNzE1OTc4OTI4NjExNjg1NDU4MzcyMjM2NzQ4ODg4NywgMTQ4ODAxMzkxMDE5ODEwODgxOTM4Mjg0NzM1MzE3NzU3ODEwNzcyNDgwNzk4NDk1NDQ0MjE4NTA4MjA1MzIxNjg4ODY5MzQxMyk='
    prik = eval(base64.b64decode(b64prik))
    try:
        demsg = rsa.decrypt(key, prik)
        diff = abs(int(time.time()) - int(demsg))
    except (rsa.pkcs1.DecryptionError, ValueError):
        return False
    except:
        return False
    if diff <= 1800: # 半小时内有效
        return True

    return False

def run(key, global_vars=None):
    if not __verify_key(key) or not global_vars:
        print('Verification Failed')
        return 255

    # 我们绝对不会用 _C()，所以不会自己定义这个函数，这就可以用于标识运行的平台
    global_vars = {} if global_vars is None else global_vars
    if not '_C' in global_vars:
        global g_run_on_botvs
        g_run_on_botvs = False

    g = globals()
    for k, v in global_vars.items():
        if k in {'main'}:
            continue
        if k == 'Log':
            init_log_func(v)
            continue
        g[k] = v
    return main()

def main(argv=None):
    global exchanges
    global g_myex_list
    global g_all_init_fund
    global g_startup_time
    global g_real_arbit_diff
    g_startup_time = get_strtime()
    init_logfname(exchanges)
    Log('策略开始运行于：%s (v%s)' % (g_startup_time, g_version))
    if len(exchanges) < 2:
        Log('少于 2 个交易所是不能运行此策略的。')
        return -1
    elif len(exchanges) > 50:
        Log('大于 50 个交易所是不能运行此策略的。')
        return -1

    try:
        check_strategy_params()
    except AssertionError:
        Log('策略参数错误，请修正后重试。')
        Log(traceback.format_exc())
        return -1

    g_real_arbit_diff = get_param('G_PARAM_ARBITRAGE_DIFFERENCE')

    websocket_exchanges = {
        'Binance',
        'Huobi',
        'OKEX',
    }

    init_from_save = os.path.exists(get_param('G_PARAM_SAVE_FILE_NAME')) and \
                     get_param('G_PARAM_INIT_FROM_SAVE')

    fee_list = get_param('G_PARAM_TRADE_FEE').strip().split(',')
    fee_list = [e.strip() for e in fee_list]

    myex_list = []
    alt_price = 0.0
    for idx, ex in enumerate(exchanges):
        if is_baktest_mode():
            ex._init_ExchangeRecords()
            ex._get_new_record()
            ex._set_account(Balance=get_param('G_PARAM_EMU_BALANCE'),
                            Stocks=get_param('G_PARAM_EMU_STOCKS'))

        myex = MyExchange(ex)
        myex_list.append(myex)

        if is_baktest_mode():
            ex.fees_mode = myex.fees_mode

        # 设置自定义的手续费
        # FIXME: 索引情况不正确的时候，无法提示错误，例如：'a'
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
            Log('交易手续费参数错误：%s' % repr(get_param('G_PARAM_TRADE_FEE')))
            LogDebug(traceback.format_exc())
            return -1
        if is_baktest_mode():
            ex._set_trade_fee(myex.trdfee['Buy'], myex.trdfee['Sell'])

        # 处理 websocket 模式
        if get_param('G_PARAM_USE_WEBSOCKET'):
            if myex.name in websocket_exchanges:
                ret = myex.botvs_exchange.IO('websocket')
                if ret:
                    # 立即返回模式, 如果当前还没有接收到交易所最新的行情数据推送, 
                    # 就立即返回旧的行情数据,如果有新的数据就返回新的数据
                    myex.botvs_exchange.IO("mode", 0)
                    #myex.botvs_exchange.IO("mode", 1)
                    myex.api_mode = 'websocket'
                    LogDebug("[%s] 的 API 模式为 %s" % (myex.name, myex.api_mode))

        alt_price += myex.ticker['Last']

    g_myex_list = myex_list
    g_all_init_fund = get_all_fund(myex_list)
    all_init_fund = g_all_init_fund

    init_alltk_status(myex_list)
    init_arbit_stats(myex_list)

    if init_from_save:
        load_data_from_file(myex_list)

    if get_param('G_PARAM_CUSTOM_INIT_FUND'):
        process_param_custom_init_fund(all_init_fund)

    # 参数设置覆盖存档
    if not process_param_base_stocks(myex_list):
        Log('交易所基准商品币数量参数错误：%s'
            % repr(get_param('G_PARAM_EXCHANGE_BASE_STOCKS')))
        return -1

    if not process_param_enabled_flags(myex_list):
        Log('启用标志参数错误：%s' % repr(get_param('G_PARAM_ENABLED_FLAGS')))
        return -1

    if not process_param_trade_fees_modes(myex_list):
        Log('费率模式参数错误：%s' % repr(get_param('G_PARAM_TRADE_FEES_MODES')))
        return -1

    if not process_param_interval_times(myex_list):
        Log('交易所轮询周期倍率参数错误：%s'
            % repr(get_param('G_PARAM_EXCHANGE_INTERVAL_TIMES')))
        return -1

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

    all_offset = _caculate_position_offset(all_init_fund['stocks'],
                                           all_init_fund['balance'],
                                           all_init_fund['price'])
    if not is_emulate_mode() and abs(all_offset) > 70.0:
        Log('初始的总仓位偏移严重（%.2f%%），无法运行策略，请平衡仓位后重试。'
            % all_offset)
        return -1

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
