#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import random
import json
import copy  

'''
{
    // 存档名称。用来储存或者读取一个存档时用的。为了并发不冲突，最好记一下。
    // 字符串(string) 数字英文皆可
    "saved_name":"saved_qtum_BTC",

    // 是否开启存档功能
    // 布尔型(true/false) 测试ing。会储存参数，降低每次学习周期
    "use_saved_chushi":true,

    // 如果需要清空，重新存档，请勾选
    // 布尔型(true/false) 测试ing。会重新储存参数
    "first_use_saved_chushi":true,

    // 启用websocket模式
    // 布尔型(true/false) 勾上启用。不勾上不启用（更稳定）
    "use_websocket":true,

    // 轮询周期
    // 数字型(number) 500以上
    "LoopInterval":1000,

    // 套利差高于手续费计算套利，还是固定套利差？
    // 布尔型(true/false) true则是手续费基础上再加套利差，否则是直接套利差（不勾就是老版本）
    "more_than_taolicha":true,

    // 初始设定搬砖的差价，百分比,建议最少为手续费的两倍
    // x/100
    "taoli_cha":0.25,

    // 套利差范围（下限）
    // 保证套利差不低于这个数字，比如比特币低于0.4会亏，以太低于0.1会亏
    "taoli_cha_min":0.2,

    // 套利差范围（上限）
    // 当阈值大于这个时不再增加
    "taoli_cha_max":1.2,

    // 一个基础单成交几个B？
    // 0.04~0.1
    "init_amount":5,

    // 把这个设置为你所有交易所中该B的的最小交易量
    // 比特币是0.1，山寨币一般是0.01
    "BorE":1,

    // 你们这些增强学习机啊，还是too young，too simple，还需要再多学习一个！
    // 建议设置500以上，一般学习一次3秒
    "One_more_learns":500,

    // 对第一个价格的接受程度
    // 1~100之间。建议10%，波动大的币种可以设定大一些。这个值越大，初始学习周期理论上来说需要的就越小。只发挥一次作用。
    "delta_delta_U1":65,

    // 滑点，代表你为了快速成交愿意额外付出多少钱
    // 你要是小气也可以设置为0
    "huadian":0.000002,

    // beta石。这个用来限制每次交易量的变动
    // 建议设置1000，这个数字越大，成交越快，越小成交单拆分越多。
    "beta_rock":700,

    // 按照真实时间动态调仓，还是搬砖时间开启趋势机？
    // 好的交易所建议按照搬砖时间，差的按照真实时间
    "real_time_count":true,

    // 控制多少次以后开放同步趋势机，建议至少100
    // 建议至少100以上，不然搬砖会受到影响
    "duibi_times_con":40,

    // 拆分百分之多少的钱用来同时趋势机，建议10以内
    // 这个值越大，搬砖机受影响越大，建议设置10以内
    "qushi_sp":1,

    // 这个数值设定后趋势机才起作用
    // 是否把一定比例的钱设置做趋势机？这个会降低搬砖机的收益，但是会一定程度上能够套时间差的利。由于现在还不能做空，处于试验阶段
    "easy_qushi":true,

    // 这个勾上以后会按实际值计算交易费率，否则是理论值。
    // 按理论值计算则速度更快，实际收益更高。按实际值计算速度会略慢一些。按理论值计算由于回调信息频率降低，抢单次数更多，实际收益更高
    "real_count_fee":true,

    // 最大差价
    // 这个对差价过大的交易所作调整用的，设置为你看到过的交易所间的最大差价。
    "jubi_yunbi_cheack_and_change":0.00005,

    // 微调价格大于平均价格多少启动趋势机
    // 1就是1乘以套利差。2就是2乘以套利差
    "little_change":2,

    // 价格的小数点后限制几位
    // 日本交易所设置为0，美国交易所设置为1
    "price_N":6,

    // 交易量的小数点后限制几位
    // 比特币一般是2，eth是1，价格越低这个也越小
    "amount_N":2,

    // 去掉kraken以后一般就不需要把这个勾上了。
    // 配合‘遇到该交易所出问题时这个交易所等待多久？’这个用的
    "is_meet_error_wait":false,

    // 遇到该交易所出问题时这个交易所等待多久？
    // 测试，因为kraken出了一个非常影响收益的问题。
    "meet_error_wait":200,

    // 学习速度。越大越快。（1，2，3，4目前这4个挡中选）
    // 对于变动慢的，就选低档，对于变动块的，比如无手续费小波段套利，就选高档。
    "cg_delta_speed":2
}
'''

g_args = {
    "args": [
        [
            "saved_name", 
            "saved_qtum_BTC"
        ], 
        [
            "use_saved_chushi", 
            False
        ], 
        [
            "first_use_saved_chushi", 
            False
        ], 
        [
            "use_websocket", 
            False
        ], 
        [
            "LoopInterval", 
            1000
        ], 
        [
            "more_than_taolicha", 
            True
        ], 
        [
            "taoli_cha", 
            0.25
        ], 
        [
            "taoli_cha_min", 
            0.2     # 0.1
        ], 
        [
            "taoli_cha_max", 
            1.2
        ], 
        [
            "init_amount", 
            5
        ], 
        [
            "BorE", 
            1
        ], 
        [
            "One_more_learns", 
            500
        ], 
        [
            "delta_delta_U1", 
            65
        ], 
        [
            "huadian", 
            2e-06
        ], 
        [
            "beta_rock", 
            700
        ], 
        [
            "real_time_count", 
            True
        ], 
        [
            "duibi_times_con", 
            40
        ], 
        [
            "qushi_sp", 
            1
        ], 
        [
            "easy_qushi", 
            True
        ], 
        [
            "real_count_fee", 
            True
        ], 
        [
            "jubi_yunbi_cheack_and_change", 
            5e-05
        ], 
        [
            "little_change", 
            2
        ], 
        [
            "price_N", 
            6
        ], 
        [
            "amount_N", 
            2
        ], 
        [
            "is_meet_error_wait", 
            False
        ], 
        [
            "meet_error_wait", 
            200
        ], 
        [
            "cg_delta_speed", 
            2
        ]
    ], 
    "period": 4, 
    "timestamp": 1515674516660
}

try:
    exchanges
except NameError:
    from emutest import *
    from emutest import _CDelay
    from emutest import _N

for i in g_args['args']:
    n = i[0]
    v = i[1]
    exec(n + ' = ' + repr(v))
    Log(n + ' = ' + repr(v))
del i, n, v

def is_emutest_mode():
    return True

# 在数据模拟测试模式下，下单后多长时间再进行下一次套利
g_wait_for_order = 10
g_loop_count = 0
g_last_order_timestamp = 0
def get_loop_count():
    global g_loop_count
    return g_loop_count

def touch_last_order_timestamp():
    global g_last_order_timestamp
    g_last_order_timestamp = get_loop_count()

def get_last_order_timestamp():
    global g_last_order_timestamp
    return g_last_order_timestamp

initAccount = None
# JYS 实例列表
jys_class_list = []
init_dict = {}
init_delta = 0
banzhuan_cha = 0
# 最近一次下单的搬砖收益
last_banzhuan_price = 0
str_frozen_id_jys = ['Quoine', 'Coincheck', 'Zaif', 'Huobi']
#debug用: 
FEE_DIC = {'Sell': 0.25,
           'Buy': 0.25 }

FEE_DIC_OTHER = { 'bitfinex':{'Sell': 0.2,'Buy': 0.2},
                  'kraken':{'Sell': 0.26,'Buy': 0.26},
                  'hitbtc':{'Sell': 0.1,'Buy': 0.1},
                  'okcoin_en':{'Sell': 0.2,'Buy': 0.2},
                 'binance':{'Sell': 0.1,'Buy': 0.1},
                 'okex':{'Sell': 0.1,'Buy': 0.1},
                 'zb':{'Sell': 0,'Buy': 0},
                 'huobi':{'Sell': 0.2,'Buy': 0.2},
                 'huobipro':{'Sell': 0.2,'Buy': 0.2},
                 'bitflyer':{'Sell': 0.01,'Buy': 0.01},
                'quoine':{'Sell': 0,'Buy': 0},
                'quoinex':{'Sell': 0,'Buy': 0},
                'coincheck':{'Sell': 0,'Buy': 0},
                'zaif':{'Sell': -0.01,'Buy': -0.01}}

wait_for_saved = { 'saved_chushi':{ 'money':0,
                                   'bi':0,
                                   'zg':0,
                                   'fist_price':0 },
                  'saved_delta':{},
                  'saved_banzhuan':banzhuan_cha,
                  'saved_jys_first_state':{}}

if use_saved_chushi and not first_use_saved_chushi:
    try:
    #if 1:
        this_saved_name1 = saved_name + '1' 
        this_saved_name2 = saved_name + '2'
    
        with open( this_saved_name1, 'r') as f:
            try:
                saved_file1 = json.load(f)
            except:
                saved_file1 = {}
        with open( this_saved_name2, 'r') as f:
            try:
                saved_file2 = json.load(f)
            except:
                saved_file2 = {}
        
        if len(saved_file1) > len(saved_file2):
            saved_file = saved_file1
        else:
            saved_file = saved_file2 
            
        chushi = saved_file['saved_chushi'] 
        banzhuan_cha = saved_file['saved_banzhuan']
        
        wait_for_saved = copy.deepcopy( saved_file )
    except:
        Log('未找到初始存档。')
        
else:
    chushi = {'money':0,
              'bi':0,
              'zg':0,
              'fist_price':0}

# 写
# - 趋势调仓买时更新 re_make_duibi_dic
# - 趋势调仓卖时更新 re_make_duibi_dic
# - let_us_trade 买/卖交易时都更新
# 读
# - 判断搬砖次数，超过 趋势阈值 后，开启趋势调仓
duibi_price = {'buy':False,
               'sale':False,
               'count_times':0}

_CDelay( 2000 ) # 容错重复轮询间隔
# 无用
qushi_action_save = []


def main():
    global chushi, wait_for_saved, for_test
    global g_wait_for_order
    global g_loop_count
    if len(exchanges)<2:
        Log(exchanges,'只有不足俩，无法套利')
    else:
        # 无用
        this_compare_dict = {} #比较用的字典
        for this_exchange in exchanges:
            if is_emutest_mode():
                this_exchange._init_ExchangeRecords()
                this_exchange._get_new_record()
                this_exchange._set_account(Stocks=20.0, Balance=0.075)
            jys = JYS(this_exchange)
            if is_emutest_mode():
                this_exchange._set_trade_fee(jys.Fee['Buy'], jys.Fee['Sell'])
            if first_use_saved_chushi: # 清空存档再重新保存
                wait_for_saved['saved_jys_first_state'][jys.name] = {}
                wait_for_saved['saved_jys_first_state'][jys.name]['first_Balance'] = jys.first_Balance
                wait_for_saved['saved_jys_first_state'][jys.name]['first_amount'] = jys.first_amount
                wait_for_saved['saved_jys_first_state'][jys.name]['traded_amount'] = jys.traded_amount
            else:
                try:
                    saved_file['saved_jys_first_state'][jys.name]
                    jys.first_Balance = saved_file['saved_jys_first_state'][jys.name]['first_Balance']
                    jys.first_amount = saved_file['saved_jys_first_state'][jys.name]['first_amount']
                    jys.traded_amount = saved_file['saved_jys_first_state'][jys.name]['traded_amount']
                    
                    Log('成功从存档【',saved_name,'】中读取交易所【',jys.name,'】的初始信息')
                except:
                    # 读取失败就用当前获取的值
                    wait_for_saved['saved_jys_first_state'][jys.name] = {}
                    wait_for_saved['saved_jys_first_state'][jys.name]['first_Balance'] = jys.first_Balance
                    wait_for_saved['saved_jys_first_state'][jys.name]['first_amount'] = jys.first_amount      
                    wait_for_saved['saved_jys_first_state'][jys.name]['traded_amount'] = jys.traded_amount
                
            
            #except_jysnames = ['BTCC','OKEX']
            if use_websocket:
                except_jysnames = ['BTCC']
                is_websocket = False
            #if jys.name in except_jysnames:
                if not jys.name in except_jysnames:
                    is_websocket = jys.exchange.IO("websocket")
                if is_websocket:
                    jys.exchange.IO("mode", 0)
                    is_websocket = "websocket"
                else:
                    is_websocket = 'REST' 
            else:
                is_websocket = 'REST' 
                
            jys.websocket_mode = is_websocket 
            # NOTE: 好像当前只有 Binance, OKEX, Huobi 支持websocket模式
            Log('当前的',jys.name,'的is_websocket为：',jys.websocket_mode )
            
            jys_class_list.append(jys)
            this_money = jys.account['Balance'] + jys.account['FrozenBalance']
            this_stock = jys.account['Stocks'] + jys.account['FrozenStocks']
            
            # 不开启(使用已有的)存档 或 重新存档
            if not use_saved_chushi or first_use_saved_chushi:
                chushi['money'] += this_money
                chushi['bi'] += this_stock
                chushi['zg'] += this_money + this_stock * jys.Ticker['Last']


        if not use_saved_chushi or first_use_saved_chushi:    
            # 平均价格，使用总共减掉总定价币数再除以商品币总数算出来的
            chushi['fist_price'] =  ( chushi['zg'] - chushi['money'] ) / chushi['bi']
            duibi_price = re_make_duibi_dic(jys_class_list,False,False)
            chushi['mc'] = min(chushi['money'] , (chushi['zg'] - chushi['money']) )
            
            Log('未使用存档，创建新存档初始值中...')
            wait_for_saved['saved_chushi'] = chushi 
            
        else:
            Log('已使用存档，使用存档值初始化中...')
            
        Log('初始总钱为：',_N( chushi['money'], price_N ),'初始总币数量为',_N( chushi['bi'], amount_N ),
            '初始仓总值为',_N( chushi['zg'], price_N ),'初始的交易所平均价格为：',_N( chushi['fist_price'], price_N) )
        
        jys_compare_list = make_compare_dict(jys_class_list) #找出所有交易所配对，不重复。
        
        
        for i in jys_compare_list:
            try:
                wait_for_saved['saved_delta'] 
            except:
                wait_for_saved['saved_delta'] = {}
            try:
                wait_for_saved['saved_delta'][i[0].name]
            except:
                wait_for_saved['saved_delta'][i[0].name] = {}
            try:
                wait_for_saved['saved_delta'][i[0].name][i[1].name]
            except:
                wait_for_saved['saved_delta'][i[0].name][i[1].name] = {}
            
            if use_saved_chushi and not first_use_saved_chushi:
                try:
                    i[0].delta_init( i[1] , init_delta )
                    
                    i[0].delta_list[i[1].name] = saved_file['saved_delta'][i[0].name][i[1].name]['delta_list']
                    i[0].delta_cg_list[i[1].name] = saved_file['saved_delta'][i[0].name][i[1].name]['delta_cg_list']
                    i[0].traded_times_dict[i[1].name] = saved_file['saved_delta'][i[0].name][i[1].name]['traded_times']
                    
                except:
                    i[0].delta_init( i[1] , init_delta )

                    i[0].delta_list[i[1].name] = saved_file['saved_delta'][i[1].name][i[0].name]['delta_list']
                    i[0].delta_cg_list[i[1].name] = saved_file['saved_delta'][i[1].name][i[0].name]['delta_cg_list']
                    i[0].traded_times_dict[i[1].name] = saved_file['saved_delta'][i[1].name][i[0].name]['traded_times']
            else:
                i[0].delta_init( i[1] , init_delta )

                wait_for_saved['saved_delta'][i[0].name][i[1].name]['traded_times_dict'] = i[0].traded_times_dict[i[1].name]
                wait_for_saved['saved_delta'][i[0].name][i[1].name]['delta_list'] = i[0].delta_list[i[1].name]
                wait_for_saved['saved_delta'][i[0].name][i[1].name]['delta_cg_list'] = i[0].delta_cg_list[i[1].name]                
                
            
            
    last_loop_time = time.time()    
    # 纯粹记录循环次数
    cishu = 0
    # 大概400次循环后可能打印盈利
    should_show = 0
    # 无用
    this_force_yingli_m2 = 0
    # 定(单)位时间内搬砖单数
    last_1000_jy_amount = 0
    # 每次循环递增1，auto_change_taolicha()返回值会重置此变量为0
    last_1000_jy_amount_cishu = 0
    # 每times_con次轮询检查一次当前是否应该调优taolicha
    times_con = 288 * len(jys_class_list)
    #Log(jys_list)
    is_traded_last = 0 
    # 额外的学习次数
    quary_more = One_more_learns
    TableManager,  table_1, table_2 = create_the_table( jys_class_list , jys_compare_list )
    #LogProfitReset(1) # 用来清空图
    while(1):
        # 中间的仅作测试用，正式版请注释掉
        for_test = cishu
        # 中间的仅作测试用，正式版请注释掉
        this_loop_time = time.time()
        # 每次循环间的差值
        this_time_cha = this_loop_time - last_loop_time
        last_loop_time = this_loop_time
        if this_time_cha*1000 > 0 and this_time_cha *1000< LoopInterval:
            if not is_emutest_mode():
                Sleep(LoopInterval)
        
        # 无用变量
        more_sleep = False
        # 大概400次循环后可能打印盈利
        should_show += 1
        # 纯粹记录循环次数，没有其他地方更改
        cishu += 1
        g_loop_count = cishu
        # 每次循环递增1，auto_change_taolicha()返回值会重置此变量为0
        last_1000_jy_amount_cishu += 1
        
        make_data_saved( wait_for_saved, chushi, jys_compare_list, banzhuan_cha) #这个函数用来储存信息
        
        for this_jys in jys_class_list:
            
            # NOTE: 暂时可无视
            if is_meet_error_wait:
                #是否需要监测错误单？
                after_trade_do_check( this_jys )
                if this_jys.error_wait >0:
                    this_jys.error_wait -= 1
                    if jys.error_wait %99 == 1:
                        Log('由于之前', jys.name, '出现了错误,这个交易所将在：',jys.error_wait +1 ,'次轮询后再参与交易。')
                    
            if cishu% 50 == 1:
                # 每50次循环就随机刷新一次？
                this_jys.account_state = 'wait_for_refresh_rd'        
                
        try:
        #if 1:
            if cishu % 99 == 1:
                # 每100次循环就清理冻结单子
                is_traded_last = del_with_frozen(jys_class_list, now_mb, easy_qushi,chushi )
        except:
            pass        
        
        
        # 控制多少次以后开放同步趋势机，建议至少100
        # 建议至少100以上，不然搬砖会受到影响
        # "duibi_times_con": 40
        # 你们这些增强学习机啊，还是too young，too simple，还需要再多学习一个！
        # 建议设置500以上，一般学习一次3秒
        # "One_more_learns":500,
        if cishu > duibi_times_con + One_more_learns:
            #Log('趋势机启动中')
            #if 1:
            try:
                bucang(jys_class_list , now_mb , chushi, cishu, easy_qushi)
            except:
                raise
                pass
        if is_emutest_mode() and cishu > 1:
            exit = False
            for myex in jys_class_list:
                if not myex.exchange._get_new_record():
                    exit = True
                    break
                #print(myex.exchange.GetTicker())
            if exit:
                Log('End in loop', cishu)
                break
        clean_data(jys_class_list)
        get_data(jys_class_list, jys_compare_list, cishu)
        all_trade_dict = make_trade_dict(jys_compare_list)

        if last_1000_jy_amount_cishu > times_con:
            #每times_con次轮询检查一次当前是否应该调优taolicha
            last_1000_jy_amount, last_1000_jy_amount_cishu = auto_change_taolicha(last_1000_jy_amount, last_1000_jy_amount_cishu) #这个用来自动控制套利差的当前值
        
        if len(all_trade_dict)>0 and cishu > quary_more \
           and get_loop_count() >= get_last_order_timestamp() + g_wait_for_order:
                        
            sorted_trade_list = sorted(all_trade_dict, key=lambda k: k['jiacha'], reverse=True)
            
            last_done_amount = 0
            for this_trade in sorted_trade_list:
                try:
                    buy_jys_stock = this_trade['buy_jys'].account['Stocks']
                    sale_jys_stock = this_trade['sale_jys'].account['Stocks']
                    buy_jys = this_trade['buy_jys']
                    sale_jys = this_trade['sale_jys']
                    
                    if sale_jys_stock > buy_jys_stock/20 and sale_jys_stock > BorE:
                        if buy_jys.error_wait > 0:
                            buy_jys.error_wait -= 1
                            if buy_jys.error_wait %37 == 1:
                                Log('由于之前', buy_jys.name, '出现了错误,这个交易所将在：',
                                    buy_jys.error_wait +1 ,'次轮询后再参与交易。')
                        elif sale_jys.error_wait > 0:
                            sale_jys.error_wait -= 1
                            if sale_jys.error_wait %37 == 1:
                                Log('由于之前', sale_jys.name, '出现了错误,这个交易所将在：',
                                    sale_jys.error_wait +1 ,'次轮询后再参与交易。')
                        else:
                            this_trade['should_less_than_list'][0] = max( this_trade['should_less_than_list'][0] - last_done_amount,0 )
                            this_trade['should_less_than_list'][1] = max( this_trade['should_less_than_list'][1] - last_done_amount,0 )
                            this_trade['should_less_than'] = min(this_trade['should_less_than_list'])
                            this_trade_Oamount = let_us_trade(this_trade)
                            # FIXME: 这里基本可以肯定搞错了，应该是累加
                            last_done_amount = last_done_amount - this_trade_Oamount
                            
                            last_1000_jy_amount += this_trade_Oamount
                            is_traded_last = 30

                except:
                    raise
                    pass
        else:
            if cishu > One_more_learns :
                if cishu%1000 ==0 :
                    Log('已经观察大盘达到指定次数，如果监测到有利差，将开始套利。当前轮询次数为：',cishu)
                elif quary_more > cishu :
                    if ( quary_more - cishu )%33 == 1:
                        Log('交易等待中，还有', quary_more - cishu ,'次重新开始交易。')
                elif quary_more == cishu:
                    Log('已经重新等待了300次，我们接着交易。')
                    
            elif cishu%40 == 1 :
                Log('当前第',cishu,'次，还有',One_more_learns -cishu,'次观察盘后开始交易。' )
            elif cishu == One_more_learns:
                Log('已经观察大盘达到指定次数，现在开始，如果检测到利差，则开始交易。当前轮询次数为：',cishu)
            
            
        if more_sleep and LoopInterval<1000:
            Sleep(1000)
        try:
        #展示层
        #if(1):
            TableManager = make_table_with ( TableManager ,  table_1 , table_2 , jys_class_list , jys_compare_list )
            now_mb =  {'money':0,
                       'bi':0,
                       'zg':0,
                       'pingjun_price':0}
            
            _num = 0
            this_force_yingli = 0
            this_all_yingli = 0
            for jys in jys_class_list:
                #Log(jys.delta_list)
                _num += 1

                this_money = jys.account['Balance'] + jys.account['FrozenBalance']
                this_stock = jys.account['Stocks'] + jys.account['FrozenStocks'] 
                now_mb['money'] += this_money
                now_mb['bi'] += this_stock
                now_mb['zg'] += this_money + this_stock * jys.Ticker['Last']
                now_mb['pingjun_price'] = (now_mb['pingjun_price'] + jys.Ticker['Last'])
                
                this_force_yingli += ( this_money - jys.first_Balance + 
                                     ( this_stock - jys.first_amount ) * jys.Ticker['Last'] )

            now_mb['pingjun_price'] = now_mb['pingjun_price']/_num
            
            this_all_yingli = now_mb['zg'] - chushi['zg']
            
            bg_words =  ( '初始定价货币为:' + str( _N(chushi['money'], price_N) ) + ',初始商品币为:' + str( _N(chushi['bi'], amount_N) ) + 
                         ' ,初始的交易所平均价格为：' + str( _N( chushi['fist_price'], price_N) ) + ' ,净值为' + str( _N(chushi['zg'], price_N) ) +
                          ',现在定价货币为' + str( _N(now_mb['money'], price_N) ) + ',现在商品币为' + str ( _N(now_mb['bi'], amount_N) ) + 
                         '，现在平均币价为：' + str( _N( now_mb['pingjun_price'] , price_N) ) + ',净值为' + str( _N(now_mb['zg'], price_N ) ) +
                         '，当前套利差为' + str(taoli_cha) + '%, 上一次所有操作总延迟为：' + str( _N(this_time_cha, 2) ) + '秒' )
            
            end_words = ( '收益率为' + str( _N(this_all_yingli/chushi['zg']*100, 2) ) + '%，搬砖收益为' + str( _N(banzhuan_cha, price_N) ) + 
                         '，单算搬砖收益率为' + str( _N(banzhuan_cha/chushi['mc']*100 , 2) ) +'%，当前价格强制平仓，与初始状态相比，超额收益为：' +
                         str( _N( this_force_yingli , price_N) ) + '，当前总盈利为' + str( _N( this_all_yingli , price_N) ) )
            if is_emutest_mode():
                if cishu % 3600 == 0:
                    TableManager.LogStatus( bg_words , end_words )
            else:
                TableManager.LogStatus( bg_words , end_words )

            if should_show > 400 and is_traded_last < 1 and ( this_force_yingli + chushi['zg']/10) > (banzhuan_cha + chushi['zg']/10) *0.5:
                should_show = 0
                #this_force_yingli_m2 = this_force_yingli*0.8
                LogProfit( this_force_yingli )
            elif cishu ==1:
                LogProfit( this_force_yingli )
            else:
                is_traded_last -= 1
        except:
            raise
            pass

def make_data_saved(this_wait_for_saved, this_chushi, this_jys_compare_list, this_banzhuan_cha):
    
    this_wait_for_saved['saved_chushi'] = this_chushi 
    this_wait_for_saved['saved_banzhuan'] = this_banzhuan_cha 
    for i in this_jys_compare_list:
        #Log( this_wait_for_saved )
        #Log( this_wait_for_saved['saved_delta'][i[0].name][i[1].name] )
        
        #Log(i[1].name)
        #Log(this_wait_for_saved['saved_delta'][i[0].name][i[1].name])
        #Log('',i[0].name, i[1].name)
        
        this_wait_for_saved['saved_delta'][i[0].name][i[1].name]['traded_times_dict'] = i[0].traded_times_dict[i[1].name]
        this_wait_for_saved['saved_delta'][i[0].name][i[1].name]['delta_list'] = i[0].delta_list[i[1].name]
        this_wait_for_saved['saved_delta'][i[0].name][i[1].name]['delta_cg_list'] = i[0].delta_cg_list[i[1].name]

        this_wait_for_saved['saved_jys_first_state'][i[0].name]['traded_amount'] = i[0].traded_amount
        this_wait_for_saved['saved_delta'][i[0].name][i[1].name]['traded_times'] = i[0].traded_times_dict[i[1].name]
    
    this_saved_name1 = saved_name + '1' 
    this_saved_name2 = saved_name + '2'
    if is_emutest_mode:
        return
    with open( this_saved_name1, 'w') as f:
        json.dump(this_wait_for_saved, f)
        #Log( this_wait_for_saved )
        #Log('成功储存文件')
    with open( this_saved_name2, 'w') as f:
        json.dump(this_wait_for_saved, f)
        #Log( this_wait_for_saved )
        #Log('成功储存备份文件。311')
        
def after_trade_do_check(jys):
    #这个用来监测发生交易后是否账户未发生变化，如果未发生，则账户接下来不参与交易。
    if jys.do_check:
        Log('开始检测:', jys.name, '...')
        jys.do_check = False
        try:
        #if 1:
            jys.get_account()
            if jys.Balance == jys.last_Balance and jys.amount == jys.last_amount :
                jys.error_times += 1
                jys.error_times = min( 5, jys.error_times ) 
                jys.error_wait = meet_error_wait* jys.error_times 
                
                Log( jys.name, '在交易时出错，接下来它暂时不参与交易', jys.error_wait )
                Log( jys.Balance,'balance right last',  jys.last_Balance ) 
                Log( jys.amount, 'amount right last', jys.last_amount  )
                Log( 'Debug-this:', jys.account )
                Log( 'Debug-last:', jys.last_account )
                
        except:
            Log( jys.name, '在监测错误信息时，获取账户信息失败，正在重试...')
            jys.error_wait = 1
    
def auto_change_taolicha(last_1000_jy_amount, last_1000_jy_amount_cishu):
    '''
    根据最近的搬砖单数微调套利差，基本确定应该为经验值

    可能修改：
        全局变量: taoli_cha
        输入参数：last_1000_jy_amount
        输入参数：last_1000_jy_amount_cishu
    '''
    global taoli_cha
    #这个函数用来控制阈值自动行动
    if taoli_cha < taoli_cha_min:
        taoli_cha = taoli_cha_min
    elif taoli_cha > taoli_cha_max:
        taoli_cha = taoli_cha_max 
    elif last_1000_jy_amount > init_amount * 25 and last_1000_jy_amount < init_amount * 50:
        # 搬砖单数在 25x < y < 50x 的时候，不调整参数，不调整套利差
        return last_1000_jy_amount ,last_1000_jy_amount_cishu
    else:
        if last_1000_jy_amount < init_amount :
            # 0x <= y < 1x 时，减套利差
            taoli_cha -= 0.004
        elif last_1000_jy_amount < init_amount * 20:
            # 1x <= y < 20x 时，减套利差
            taoli_cha -= 0.001
        elif last_1000_jy_amount > init_amount * 100:
            # 100x < y < +∞，加套利差
            taoli_cha += 0.015
        elif last_1000_jy_amount > init_amount * 50:
            # 50x < y <= 100x，加套利差
            taoli_cha += 0.002
        ## FIXME: 20x <= y < 50x 这种情况没处理? (结合25x < y < 50x)
        ## 实际为 20x <= y <= 25x 这种情况没有处理（不调整套利差）
        # 单位时间内的搬砖单数(?)
        Log('检测到定位时间内搬砖单数为:',last_1000_jy_amount,"；启动阈值更新，更新后的阈值为:",taoli_cha)
        # 重置参数
        # 根据理解，当 0 <= y < 25x 且 50x < y < +∞时，重置输入参数
        return 0,0
    
    return last_1000_jy_amount ,last_1000_jy_amount_cishu

def create_the_table( jys_list , jys_compare_list ):
    #这个函数用来制造表单框架 
    jys_num = len(jys_list)
    col_name_list_1 = [ '交易所','当前买1价','当前卖1价','余钱','余币数量','可购买币数量','交易所延迟','模式','买卖手续费(%)','套利数量' ]
    col_name_list_2 = [ '交易所路径' , '两交易所目前买卖价格信息','该路径套利数量' ]
    
    #创建表单类
    TbM  = CreateTableManager()
    
    #添加具体的两个表单，列长为头名，行长为交易所（交易所对）个数
    table_1 = TbM.AddTable("交易所状态信息", len(col_name_list_1), jys_num) 
    table_2 = TbM.AddTable("交易所搬砖路径", len(col_name_list_2), len(jys_compare_list)) 
    
    #设定具体的头名称
    table_1.SetCols( col_name_list_1 )
    table_2.SetCols( col_name_list_2 )
    
    _this_counts = 0
    for jys in jys_list:
        _this_counts += 1
        table_1.SetColRow( 1, _this_counts , jys.name )
        
        
    _this_counts = 0    
    for jys_compare in jys_compare_list:
        _this_counts += 1
        jys_a = jys_compare[0].name 
        jys_b = jys_compare[1].name
        this_word = str(jys_a) + ' 和 ' + str(jys_b)
        table_2.SetColRow( 1, _this_counts , this_word )
        
    return TbM , table_1 , table_2
        
    
def make_table_with( TbM ,  table_1 , table_2 , jys_list , jys_compare_list ):
    #这个函数用来提取交易所数据放入展示用表单 
    
    _this_counts = 0
    for jys in jys_list:
        #这个用来填入余钱，余币等表1的数据
        _this_counts += 1
        table_1.SetColRow( 2 , _this_counts , _N( jys.buy_1 , price_N) )
        table_1.SetColRow( 3 , _this_counts , _N( jys.sale_1 , price_N) )
        table_1.SetColRow( 4 , _this_counts , _N( jys.Balance , price_N) )
        table_1.SetColRow( 5 , _this_counts , jys.amount )
        table_1.SetColRow( 6 , _this_counts , jys.can_buy )
        
        if jys.ping == 0:
            table_1.SetColRow( 7 , _this_counts ,'----')
        else:
            table_1.SetColRow( 7 , _this_counts , str( _N( jys.ping, 1) ) +' ms')
            
        table_1.SetColRow( 8 , _this_counts , jys.websocket_mode )
        table_1.SetColRow( 9 , _this_counts , str( '买单：'+str(jys.Fee['Buy'])+'% ,卖单:'+ str(jys.Fee['Sell']) + '%') )
        table_1.SetColRow( 10 , _this_counts , _N(jys.traded_amount, amount_N) )
        
    _this_counts = 0    
    for jys_compare in jys_compare_list:
        _this_counts += 1
        jys_a = jys_compare[0] 
        jys_b = jys_compare[1]
        
        a_buy1 , a_sale1 = _N( jys_a.buy_1 , price_N ) , _N( jys_a.sale_1 , price_N )
        b_buy1 , b_sale1 = _N( jys_b.buy_1 , price_N ) , _N( jys_b.sale_1 , price_N )
        
        abuy_bsale_cha = b_sale1 - a_buy1
        asale_bbuy_cha = a_sale1 - b_buy1
        
        this_delta = jys_a.delta_list[jys_b.name]
        #this_delta = 0.0
        
        differ = abs(jys_a.Ticker['Last'] - jys_b.Ticker['Last'])
        if differ> jubi_yunbi_cheack_and_change*0.7:
            this_might_kk = _N( (differ/jubi_yunbi_cheack_and_change + 1)*taoli_cha, price_N)
        else:
            this_might_kk = taoli_cha
            
        if more_than_taolicha:
            fee_asbb = jys_a.Fee['Sell'] + jys_b.Fee['Buy'] + this_might_kk
            fee_abbs = jys_a.Fee['Buy'] + jys_b.Fee['Sell'] + this_might_kk
            acha = a_sale1 - b_buy1*( 1+fee_asbb * 1.0 /100 ) - this_delta 
            bcha = b_sale1 - a_buy1*( 1+fee_abbs * 1.0 /100 ) + this_delta  
            
            if bcha > 0:
                pycha = _N( - this_delta + a_buy1*( fee_abbs * 1.0 /100 ) , price_N )
                words = ( jys_a.name +'当前买1价为' + str(a_buy1) + ',' + jys_b.name + ',当前卖1价为' + str(b_sale1) + 
                     '大于差价' + str( pycha ) + ',从价格来看可从' + jys_a.name + '买' + jys_b.name + '卖' )
                
            elif acha > 0 :    
                pycha = _N( this_delta + b_buy1 *( fee_asbb * 1.0 /100 ) , price_N )
                words = ( jys_a.name +'当前卖1价为' + str(a_sale1) + ',' + jys_b.name + ',当前买1价为' + str(b_buy1) + 
                     '大于差价' + str( pycha ) + ',从价格来看可从' + jys_a.name + '卖' + jys_b.name + '买' )
                
            else:
                pycha1 = _N( - this_delta + a_buy1*( fee_abbs * 1.0 /100 ) , price_N )
                pycha2 = _N( this_delta + b_buy1 *( fee_asbb * 1.0 /100 ) , price_N )
                words = ( jys_a.name +'当前买1价为' + str(a_buy1) + ',' + jys_b.name + '当前卖1价为' + str(b_sale1) + ' ; ' +
                         jys_a.name +'当前卖1价为' + str(a_sale1) + ',' + jys_b.name + '当前买1价为' + str(b_buy1) + 
                         ' ; 目前两交易所偏移差价分别为：'+  str( pycha1 )+'和' + str( pycha2 ) +
                         '; 算上当前设定阈值和手续费，从价格来看无成交机会' )
        else:        
            if abuy_bsale_cha > - this_delta + a_buy1 * this_might_kk / 100  :
                pycha = _N( ( -this_delta + a_buy1 * this_might_kk / 100) , price_N)
                words = ( jys_a.name +'当前买1价为' + str(a_buy1) + ',' + jys_b.name + ',当前卖1价为' + str(b_sale1) + 
                         '大于差价' + str( pycha ) + ',从价格来看可从' + jys_a.name + '买' + jys_b.name + '卖' )
                
            elif asale_bbuy_cha > this_delta + b_buy1 * this_might_kk / 100 :
                pycha = _N( ( this_delta + b_buy1 * this_might_kk / 100) , 2)
                words = ( jys_a.name +'当前卖1价为' + str(a_sale1) + ',' + jys_b.name + ',当前买1价为' + str(b_buy1) + 
                     '大于差价' + str( pycha ) + ',从价格来看可从' + jys_a.name + '卖' + jys_b.name + '买' )
            else:
                pycha1 = _N( (-this_delta + ( a_buy1  ) * this_might_kk / 200) , price_N )
                pycha2 = _N( (this_delta + ( b_buy1 ) * this_might_kk / 200) , price_N )
                words = ( jys_a.name +'当前买1价为' + str(a_buy1) + ',' + jys_b.name + '当前卖1价为' + str(b_sale1) + ' ; ' +
                      jys_a.name +'当前卖1价为' + str(a_sale1) + ',' + jys_b.name + '当前买1价为' + str(b_buy1) + 
                     ' ; 目前两交易所偏移差价分别为：'+  str( pycha1 )+'和' + str( pycha2 ) +
                     '; 算上当前设定阈值和手续费，从价格来看无成交机会' )
        
        table_2.SetColRow( 2, _this_counts , words )
        
        jys_a_b_treaded_words = _N( jys_a.traded_times_dict[jys_b.name] ,3)
        table_2.SetColRow( 3, _this_counts , jys_a_b_treaded_words )

    return TbM

def re_make_duibi_dic(jys_list,last_buy,last_sale):
    #这个函数用来重设对照表
    duibi_price = {'buy':False,
               'sale':False,
               'count_times':0}
    
    # 没搞懂这个 对比价格 啥意思
    # 意思好像是每个交易所的价格“加权”累加，但是第一个循环的时候价格减半了
    # FIXME: 第一次循环疑似有问题
    for jys in jys_list:
        try:
            # NOTE: 貌似不可能发生错误...
            duibi_price['buy'] = duibi_price['buy'] * 0.5 + jys.Ticker['Buy'] * 0.5
            duibi_price['sale'] = duibi_price['sale'] * 0.5 + jys.Ticker['Sell'] * 0.5
            
            jys.duibi_price['buy'] = jys.duibi_price['buy'] * 0.5 + jys.Ticker['Buy'] * 0.5
            jys.duibi_price['sale'] = jys.duibi_price['sale'] * 0.5 + jys.Ticker['Sell'] * 0.5 
            
        except:
            Log('好像发生了很少见的情况...')
            raise
            if last_buy:
                duibi_price['buy'] = last_buy
                jys.duibi_price['buy'] = last_buy
            else:
                duibi_price['buy'] = jys.Ticker['Buy']
                jys.duibi_price['buy'] = jys.Ticker['Buy']
                
            if last_sale:
                duibi_price['sale'] = last_sale
                jys.duibi_price['sale'] = last_sale
            else:
                duibi_price['sale'] = jys.Ticker['Sell'] *1.1
                jys.duibi_price['sale'] = jys.Ticker['Sell'] *1.1
            duibi_price['count_times'] = 0
            jys.duibi_price['count_times'] = 0
    return duibi_price
        
def make_trade_dict(jys_compare_list):
    #这个函数用来计算应该产生的订单
    all_trade_dict = []
    for i in jys_compare_list:
        #Log(i[0].name)
        try:
            if i[0].ping<2000 and i[1].ping<2000:
                one_trade_tic = i[0].make_trade_with_amount(i[1] ,hua_dian = huadian)
                if one_trade_tic:
                    all_trade_dict.append(one_trade_tic)
        except:
            raise
            if i[0].Depth and i[1].Depth:
                try:
                    Log('在制作', i[0].name, '-->',i[1].name,'交易对时出错了。')
                    Log(i[0].name, '0...')
                    Log(i[0].name, 'stock:' ,i[0].account['Stocks'])
                    Log(i[0].name, 'balance:', i[0].account['Balance'])
                    Log(i[0].name, 'ask[0]:', i[0].Depth['Asks'][0])
                    Log(i[0].name, 'all_ask:', i[0].Depth['Asks'])
                    Log(i[0].name, 'bids[0]', i[0].Depth['Bids'][0])
                    Log(i[0].name, 'all_bids', i[0].Depth['Bids'])

                    Log(i[1].name, '1...')
                    Log(i[1].name, 'stock:' , i[1].account['Stocks'])
                    Log(i[1].name, 'balance:', i[1].account['Balance'])
                    Log(i[1].name, 'ask[0]:', i[1].Depth['Asks'][0])
                    Log(i[1].name, 'all_ask:', i[1].Depth['Asks'])
                    Log(i[1].name, 'bids[0]', i[1].Depth['Bids'][0])
                    Log(i[1].name, 'all_bids', i[1].Depth['Bids'])
                except:
                    #try:
                    #    if not i[0].Depth:
                    #        Log('未获取到',i[0].name,'的深度')
                    #    if not i[1].Depth:
                    #        Log('未获取到',i[1].name,'的深度')
                    #except:
                    pass
            
    return all_trade_dict

def get_data(jys_list, jys_compare_list, cishu ):
    this_jysname = None
    #只更新wait_for_refresh状态的交易所的account数据，以降低延迟
    for i in jys_list:
        if i.account_state == 'wait_for_refresh' or i.account == 'wait_for_refresh' or cishu == 1 :
            #if i.account_state == 'wait_for_refresh' :
                #Log('更新了状态信息：', i.name)
            #if 1:
            try:
                time_0 = time.time()
                this_jysname = i.name 
                i.get_account()
                i.account_state == 'Done'
                i.ping += _N( time.time() - time_0, 4)*1000
            except:
                i.account_state = 'wait_for_refresh' 
                Log( this_jysname,':获取account数据失败')
                
        elif  i.account_state == 'wait_for_refresh_rd' :
            rd_time = 10
            if i.name in ['Quoine','Zaif','Bitfinex']: 
                rd_time = 3
            if random.random()*100 < rd_time:
                try:
                #if 1:
                    time_0 = time.time()
                    i.get_account()
                    i.account_state = 'Done'
                    i.ping += _N( time.time() - time_0, 4)*1000
                except:
                    Log( this_jysname,':随机获取account数据失败')
                
    this_jysname = None
    for i in jys_list:
        #接下来获取ticker数据
        error_pos = 0
        #if 1:
        try:
            time_0 = time.time()   
            this_jysname = i.name
            error_pos = 1
            i.get_ticker()
            #error_pos = 2
            #i.get_account()
            #error_pos = 3
            #i.get_depth()
            i.ping += _N( time.time() - time_0, 4)*1000
        except:
            raise
            pass
            #Log('this_jysname',this_jysname,':',error_pos)

    if is_emutest_mode():
        for i in jys_list:
            time_0 = time.time()
            i.get_depth()
            i.ping += _N( time.time() - time_0, 4)*1000
        return

    try:       
        does_he_need_depth(jys_compare_list)
    except:
        Log('检测是否需要获取深度信息时发生错误')
    for i in jys_list:
    #接下来获取depth数据：
        if i.need_depth and cishu> LoopInterval:
            #if 1:
            try:
                time_0 = time.time()
                #Log('开始获取', i.name, '的深度信息')
                i.get_depth()
                i.ping += _N( time.time() - time_0, 4)*1000
                i.need_depth = False
            except:
                Log(i.name, '获取深度信息出错')
        
        
def does_he_need_depth(jys_compare_list):
    #现在判断是否需要获取深度信息
    for i in jys_compare_list:
        a = i[0]
        b = i[1]
        aTicker = a.Ticker 
        bTicker = b.Ticker 
        price_alast, price_asell, price_abuy = aTicker['Last'] , aTicker['Buy'] , aTicker['Sell']
        price_blast, price_bsell, price_bbuy = bTicker['Last'] , bTicker['Buy'] , bTicker['Sell']
        
        differ = price_alast - price_blast
        a.cg_delta(b.name,differ)
        delta = a.delta_list[ b.name ]
        #Log(a.name, '-->', b.name, 'delta:', delta, '; differ:', differ  )
        if differ> jubi_yunbi_cheack_and_change*0.7:
            this_might_kk =_N( (abs(differ)/jubi_yunbi_cheack_and_change + 1)*taoli_cha , price_N )
        else:
            this_might_kk = taoli_cha
            
        if more_than_taolicha:
            fee_asbb = a.Fee['Sell'] + b.Fee['Buy'] + taoli_cha
            fee_abbs = a.Fee['Buy'] + b.Fee['Sell'] + taoli_cha
            acha = price_asell - price_bbuy*( 1+fee_asbb * 1.0 /100 ) - delta 
            bcha = price_bsell - price_abuy*( 1+fee_abbs * 1.0 /100 ) + delta
        else:    
            acha = price_asell - price_bbuy*( 1+this_might_kk * 1.0 /100 ) - delta
            bcha = price_bsell - price_abuy*( 1+this_might_kk * 1.0 /100 ) + delta
        
        if   acha > 0 and a.amount > BorE and b.can_buy > BorE :
            i[0].need_depth = True
            i[1].need_depth = True 
        elif bcha > 0 and b.amount > BorE and a.can_buy > BorE :
            i[0].need_depth = True
            i[1].need_depth = True 
            
def clean_data(jys_list):
    for i in jys_list:
        i.cleanAT()

def bucang(jys_class_list , now_mb , chushi, now_cishu, easy_qushi):
    global duibi_price , qushi_action_save
    #这个函数用来平仓，即使得当前的币数量等于初始数量
    all_fbalance = 0    # 总共的冻结余额（定价币）
    all_fstock = 0      # 总共的冻结商品币
    buy_dict = {}
    sale_dict = {}
    for jys in jys_class_list:
        this_jysname = jys.name
        this_cansale_price = jys.Ticker['Buy']
        this_cansale_amount = jys.account['Stocks']
        this_canbuy_price = jys.Ticker['Sell']
        # 为了处理浮点小数问题，需要乘以一个系数？
        this_canbuy_stock = jys.account['Balance'] / this_canbuy_price *0.999 
        all_fbalance += jys.account['FrozenBalance']
        all_fstock += jys.account['FrozenStocks']
        
        used_sale_price = jys.duibi_price['sale']
        used_buy_price = jys.duibi_price['buy']
        
        salep_list = {}
        buyp_list = {}
        try:
            if salep_list['amount']  < this_cansale_amount and used_sale_price < this_cansale_price:
                # NOTE: 这个分支永远进不来
                salep_list['price'] = this_cansale_price
                salep_list['amount'] = this_cansale_amount
                salep_list['jys'] = jys 
                salep_list['jys_name'] = this_jysname 
                salep_list['used_sale_price'] = used_sale_price
        except:
            salep_list['price'] = this_cansale_price
            salep_list['amount'] = this_cansale_amount
            salep_list['jys'] = jys 
            salep_list['jys_name'] = this_jysname         
            salep_list['used_sale_price'] = used_sale_price
        try:
            if buyp_list['amount'] < this_canbuy_stock and used_buy_price > this_canbuy_price:
                # NOTE: 这个分支永远进不来
                buyp_list['price'] = this_canbuy_price
                buyp_list['amount'] = this_canbuy_stock
                buyp_list['jys'] = jys 
                buyp_list['jys_name'] = this_jysname    
                buyp_list['used_buy_price'] = used_buy_price
        except:
            buyp_list['price'] = this_canbuy_price
            buyp_list['amount'] = this_canbuy_stock
            buyp_list['jys'] = jys 
            buyp_list['jys_name'] = this_jysname 
            buyp_list['used_buy_price'] = used_buy_price
    
    if easy_qushi:
        ping_amount = now_mb['zg']/now_mb['pingjun_price']
        ping_amount = _N( ping_amount/2 , amount_N + 1) # 币钱平仓后应有的币
    else:
        ping_amount = chushi['bi']
        
    qushi_do_it = False 
    if real_time_count: 
        if now_cishu % ( duibi_times_con * 30 ) == 0: 
            qushi_do_it = True 
    else: 
        if duibi_price['count_times'] > duibi_times_con: 
            qushi_do_it = True 
    
    # 冻结商品币不足当前总商品币的 10% 并且 当前商品币总量不足平仓需要的商品币量
    if all_fstock < 0.1 * now_mb['bi'] and now_mb['bi'] < (1.0 + qushi_sp *1.0/100) * ping_amount:
        # 当前买价低于之前对比买价（算上套利差）时，才执行交易
        if buyp_list['price'] < buyp_list['used_buy_price'] * ( 1 - little_change*taoli_cha/100 ) and qushi_do_it:
            #上方的0.98控制趋势机低于之前平均售价的多少时购买 
            this_amount = abs( ( 1+qushi_sp *1.0/100 ) * ping_amount - now_mb['bi'] )*0.6
            this_amount = min( buyp_list['amount'] ,this_amount )
            this_amount = _N(this_amount, amount_N)            
            if this_amount > BorE:
                buyp_list['jys'].buy( buyp_list['price'] , this_amount )
                Log('趋势机启动，该次购买了', this_amount ,'单，平仓amount is',ping_amount)
                #Log('清零前：',duibi_price)
                duibi_price = re_make_duibi_dic(jys_class_list,buyp_list['price'],False)
                #Log('清零后：',duibi_price)
                qushi_action_save.append({'price':buyp_list['price'],
                                          'amount':this_amount,
                                          'type':'buy'})
            
    elif all_fbalance < 0.1 * now_mb['money'] and now_mb['bi'] > ( 1-qushi_sp *1.0/100 ) * ping_amount:
        if salep_list['price'] > salep_list['used_sale_price'] * (1 + little_change*taoli_cha/100) and qushi_do_it:            
            this_amount = abs( now_mb['bi'] - ( 1-qushi_sp *1.0/100 ) * ping_amount )*0.6
            this_amount = min( salep_list['amount'] ,this_amount )
            this_amount = _N(this_amount, amount_N)
            if this_amount > BorE:
                salep_list['jys'].sale( salep_list['price'], this_amount )
                Log('趋势机启动，该次卖出了', this_amount ,'单，平仓amount is', ping_amount)
                #Log('清零前：',duibi_price)
                duibi_price = re_make_duibi_dic(jys_class_list,False,salep_list['price'])
                qushi_action_save.append({'price':salep_list['price'],
                                          'amount':this_amount,
                                          'type':'sale'})
                #Log('清零后：',duibi_price)
        
def del_with_frozen(jys_list, now_mb, easy_qushi,chushi ):
    #这个函数用来处理冻结的单子,明天起来写好
    global banzhuan_cha, last_banzhuan_price
    buy_list = []
    sale_list = []
    all_buy_amount = 0
    all_sale_amount = 0
    _do_check  = False
    is_traded_last = 0
    for jys in jys_list:
        try:
            if jys.name == 'Zaif':
                #为了处理zaif的nounce问题，我们等一秒: 
                jys.last_time_stamp = make_zaif_nounce_problem( jys.last_time_stamp )   
            those_order = jys.exchange.GetOrders()
        except:
            those_order = jys.exchange.GetOrders()
        try:
            this_Ticker = jys.exchange.GetTicker()
        except:
            this_Ticker = jys.exchange.GetTicker()            
            
        this_jysname = jys.name
        if len(those_order) > 0:
            is_traded_last = 10 #标注由于进行了交易，等5回合再获取信息
            frozen_dict = {}
            for one_order in those_order:
                this_amount = _N(one_order['Amount'] - one_order['DealAmount'] , amount_N)
                if one_order['Type'] == 0:
                    last_avg_price = one_order['Price']
                    
                    try:
                        this_cancled = False
                        if jys.name == 'Zaif':
                            #为了处理zaif的nounce问题，我们等一秒: 
                            jys.last_time_stamp = make_zaif_nounce_problem( jys.last_time_stamp )   
                        #this_cancled = jys.exchange.CancelOrder( str(one_order['Id']) )
                        if jys.name in str_frozen_id_jys:
                            this_cancled = jys.exchange.CancelOrder( str(one_order['Id']) )
                        else:
                            this_cancled = jys.exchange.CancelOrder( one_order['Id'] )
                    except:
                        Log('出BUG了，未能取消单：',one_order)
                        Log('请检查是否api没给取消交易单的权限。', jys.name)
                        
                    if this_cancled:
                        jys.account['Balance'] += jys.account['FrozenBalance']
                        jys.account['FrozenBalance'] = 0
                        this_jys = {}
                        this_jys['jys'] = jys
                        this_jys['jys_name'] = this_jysname
                        this_jys['type'] = 'buy' 
                        this_jys['amount'] = this_amount
                        this_jys['last_price'] = last_avg_price
                        this_jys['price'] = this_Ticker['Sell'] 
                        buy_list.append(this_jys)
                        all_buy_amount += this_amount
                        Log('取消了',this_jysname,'的',this_amount,'冻结买单,当前累积买单数量为：',all_buy_amount)
                        #Log(buy_list)
                        _do_check = True
                        
                elif one_order['Type'] == 1:
                    last_avg_price = one_order['Price']
                    
                    try:
                        this_cancled = False
                        if jys.name == 'Zaif':
                            #为了处理zaif的nounce问题，我们等一秒: 
                            jys.last_time_stamp = make_zaif_nounce_problem( jys.last_time_stamp )                          
                        #this_cancled = jys.exchange.CancelOrder( str(one_order['Id']) )
                        if jys.name in str_frozen_id_jys:
                            this_cancled = jys.exchange.CancelOrder( str(one_order['Id']) )
                        else:
                            this_cancled = jys.exchange.CancelOrder( one_order['Id'] )
                    except:
                        Log('出BUG了，未能取消单：',one_order)
                        Log('请检查是否api没给取消交易单的权限。', jys.name)
                        
                    if this_cancled:
                        jys.account['Stocks'] += jys.account['FrozenStocks'] 
                        jys.account['FrozenStocks'] = 0
                        
                        jys.account['Stocks'] += this_amount
                        this_jys = {}
                        this_jys['jys'] = jys
                        this_jys['jys_name'] = this_jysname
                        this_jys['type'] = 'sale' 
                        this_jys['amount'] = this_amount
                        this_jys['last_price'] = last_avg_price
                        this_jys['price'] = this_Ticker['Buy']
                        sale_list.append(this_jys)
                        all_sale_amount += this_amount
                        Log('取消了',this_jysname,'的',this_amount,'冻结卖单,当前累积卖单数量为：',all_sale_amount)
                        #Log(sale_list)
                        _do_check = True
    if easy_qushi:                    
        ping_amount = now_mb['zg'] / now_mb['pingjun_price']
        ping_amount = _N( ping_amount*0.5 , amount_N +1 ) # 币钱平仓后应有的币    
    else:
        ping_amount = chushi['bi']
        
    if all_buy_amount > all_sale_amount:        
        this_amount = all_buy_amount - all_sale_amount
        i=0
        Log('正在处理冻结买单,处理数量：',this_amount)
        not_deal = False
        
        if now_mb['bi'] - this_amount*0.6 > ping_amount*0.98 :
            #Log( now_mb )
            Log ('当前币多于平币钱均衡容忍范围的币，撤销即可不需要买入，最大容忍', ping_amount*0.98 + this_amount*0.6 ) 
            this_amount = 0 
            not_deal = True
        else:
            while( this_amount > BorE):
                jys = buy_list[i]['jys']
                jys_amount = buy_list[i]['amount']
                jys_price = buy_list[i]['price']
                jys_last_price = buy_list[i]['last_price']
                jy_type = buy_list[i]['type']
                jys_name = buy_list[i]['jys_name']
                xuyimiao(jys_name)
                this_amount = jys_fchongfubuy( jys, jys_amount, this_amount, jys_price, jy_type )
                i+=1
                
        last_banzhuan_cha = banzhuan_cha * 1.0
        
        for_minus = last_banzhuan_price*0.5*( all_buy_amount - all_sale_amount )/( all_buy_amount )
        
        if not not_deal: 
            i_dif = abs(( jys_last_price - jys_price )/jys_price)*100
            i_dif = i_dif / jys.diff_might_k
            for_minus = min( for_minus * i_dif, last_banzhuan_price*0.5 )
            
        banzhuan_cha = banzhuan_cha - for_minus
        if last_banzhuan_price!= 0 :
            Log('由于未完全成交，扣除部分搬砖收益...',_N(last_banzhuan_cha, price_N),'---->',_N(banzhuan_cha, price_N) )
            last_banzhuan_price = 0
        
    elif all_buy_amount < all_sale_amount :
        this_amount = (all_sale_amount - all_buy_amount)
        i=0
        Log('正在处理冻结卖单,处理数量：',this_amount)
        not_deal = False
        if now_mb['bi'] + this_amount* 0.6 < ping_amount*1.02 :
            #Log( now_mb )
            Log ('当前币小于平币钱均衡容忍范围内的币，撤销即可不需要卖出，最大容忍',ping_amount*1.02 - this_amount* 0.6)
            this_amount = 0
            not_deal = True
        else:
            while( this_amount > BorE):
                jys = sale_list[i]['jys']
                jys_amount = sale_list[i]['amount']
                jys_last_price = sale_list[i]['last_price']
                jys_price = sale_list[i]['price']
                jy_type = sale_list[i]['type']
                jys_name = sale_list[i]['jys_name']
                xuyimiao(jys_name)
                this_amount = jys_fchongfubuy( jys, jys_amount, this_amount, jys_price, jy_type )
                i+=1
                
        last_banzhuan_cha = banzhuan_cha  * 1.0
        
        for_minus = last_banzhuan_price*0.5*(all_sale_amount - all_buy_amount)/( all_sale_amount)
        if not not_deal: 
            i_dif = abs(( jys_last_price - jys_price )/jys_price)*100
            i_dif = i_dif / jys.diff_might_k
            for_minus = min( for_minus * i_dif, last_banzhuan_price*0.5 )
            
        banzhuan_cha = banzhuan_cha - for_minus
        if last_banzhuan_price!= 0 :
            last_banzhuan_price = 0
            Log('由于未完全成交，扣除部分搬砖收益...',_N(last_banzhuan_cha, price_N),'---->',_N(banzhuan_cha, price_N) )
            
        
    elif _do_check:
        Log('冻结买单数量为:',all_buy_amount,'冻结卖单数量为',all_sale_amount,'冻结的买单卖单数量相同，直接取消即可。')
        last_banzhuan_cha = banzhuan_cha  * 1.0
        banzhuan_cha = banzhuan_cha - last_banzhuan_price
        Log('由于未完全成交，扣除部分搬砖收益...',_N(last_banzhuan_cha, price_N),'---->',_N(banzhuan_cha, price_N) )
        last_banzhuan_price = 0
        
    for jys in jys_list:
        #jys.account_state = 'wait_for_refresh'
        jys.do_check = False
     
    return is_traded_last


def jys_fchongfubuy( jys, jys_amount, this_amount, jys_price, jy_type ):
    dealed = False
    if jys_amount < this_amount:
        if jy_type == 'buy':
            dealed = jys.buy( jys_price + huadian ,jys_amount)
        elif jy_type == 'sale':
            dealed = jys.sale( jys_price - huadian ,jys_amount)
        else:
            raise
            Log('交易所订单信息出现错误，dfb-331')
        Log('余amount 为：',this_amount-jys_amount)
        if dealed:
            return this_amount-jys_amount
        else:
            return this_amount
    else:
        if jy_type == 'buy':
            dealed = jys.buy( jys_price + huadian, this_amount)
        elif jy_type == 'sale':
            dealed = jys.sale( jys_price - huadian ,this_amount)
        else:
            raise
            Log('交易所订单信息出现错误，dfb-331')
        if dealed :
            return 0        
        else:
            return this_amount
        
def xuyimiao(jys_name):
    if jys_name  == 'BTCTrade':
        Sleep(1000)
                    
def let_us_trade(trade_dict):
    #这个函数用来交易
    global banzhuan_cha, last_banzhuan_price
    sale_jys = trade_dict['sale_jys']
    buy_jys = trade_dict['buy_jys']
    
    buy_price = trade_dict['buy_price']
    sale_price = trade_dict['sales_price']

    Oamount = trade_dict['Oamount']
    yuzhi = BorE 
    
    if Oamount > trade_dict['should_less_than']:
        Oamount = trade_dict['should_less_than']
        
    if  Oamount >= yuzhi :
        #Log('Oamount',Oamount,'yuzhi',yuzhi)
        try:
            this_buy_id = buy_jys.buy( buy_price , Oamount )
        except:
            raise
            buy_jys.error_times += 1
            buy_jys.error_times = min( 5, buy_jys.error_times )
            buy_jys.error_wait = meet_error_wait* buy_jys.error_times
            Log( buy_jys.name, '出错了，接下来它暂时不参与交易')
            
        duibi_price['buy'] = duibi_price['buy'] * 0.8 + buy_price * 0.2
        buy_jys.traded_amount += Oamount 
        try:
            this_sale_id = sale_jys.sale( sale_price , Oamount )
        except:
            raise
            sale_jys.error_times += 1
            sale_jys.error_times = min( 5, sale_jys.error_times ) 
            sale_jys.error_wait = meet_error_wait* wait_count
            Log( sale_jys.name, '出错了，接下来它暂时不参与交易')
            
        duibi_price['sale'] = duibi_price['sale'] * 0.8 + sale_price * 0.2
        sale_jys.traded_amount += Oamount 
        
        if trade_dict['way'] == 'a2b':
            sale_jys.traded_times_dict[buy_jys.name] += Oamount 
        elif trade_dict['way'] == 'b2a':
            buy_jys.traded_times_dict[sale_jys.name] += Oamount 
        else:
            Log('trade_dict:',trade_dict)
        duibi_price['count_times'] += Oamount * 30
        
        if real_count_fee:
            this_fee = ( sale_price*sale_jys.Fee['Sell'] + buy_price*buy_jys.Fee['Buy'] )*Oamount/100
            last_banzhuan_price = (sale_price - buy_price )*Oamount - this_fee
        else:
            last_banzhuan_price = (sale_price - buy_price )*Oamount * ( taoli_cha - sale_jys.Fee['Sell'] - buy_jys.Fee['Buy'] )/taoli_cha
            
        banzhuan_cha += last_banzhuan_price 
    
    return Oamount      
        #LogStatus('以',buy_price,'的价格从',buy_jys.name ,'买入，以',sale_price,'的价格从',sale_jys.name ,'卖出',Oamount)
        
def make_compare_dict(exchanges):
    #这个函数用来把exchanges里的所有配对配出来,返回dict
    jys_compare_list = []
    m = len(exchanges)-1
    for i in range(m):
        for j in range(m-i):
            #Log(i,j+i+1,exchanges[i].name,exchanges[j+i+1].name)
            #jys_compare_list.append( (exchanges[i].name,exchanges[j+i+1].name) )
            jys_compare_list.append( (exchanges[i],exchanges[j+i+1]) )
    return jys_compare_list 

class JYS:
    def __init__(self,this_exchange ):
        #初始化
        self.exchange = this_exchange
        self.last_time_stamp = time.time()
        try:
            self.name = self.exchange.GetName ()
        except:
            self.name = self.exchange.GetName ()
            
        # FIXME: 看起来会有编码问题，可能是python3和python2的问题
        try:
            Log('A', self.name,'type:', type(self.name))
            self.name = self.name.decode(encoding="utf-8")
        except:
            Log('B', self.name, 'type: str' )
            self.name = str( self.name )
        self.name = str( self.name )
        
        # 初始化即获取 ticker，account，depth
        try:
            self.Ticker =  self.exchange.GetTicker ()
        except:
            self.Ticker =  self.exchange.GetTicker ()
            
        try:
            self.account = self.exchange.GetAccount ()
        except:
            self.account = self.exchange.GetAccount ()
            
        try:
            self.Depth = self.exchange.GetDepth ()
        except:
            self.Depth = self.exchange.GetDepth ()
            
        try:
            self.Fee = FEE_DIC_OTHER[self.name.lower()]
        except:
            self.Fee = FEE_DIC
        # 可能的取值 'wait_for_refresh', 'wait_for_refresh_rd', 'Done'
        # rd 标识 random（随机） 的意思
        self.account_state = 'wait_for_refresh'
        self.first_Balance = self.account['Balance'] 
        self.first_amount = self.account['Stocks']
        self.first_price = self.Ticker['Last']
        # FIXME: 这个赋值貌似反了
        self.buy_1 = self.Ticker['Sell']
        self.sale_1 = self.Ticker['Buy'] 
        
        self.do_check = False
        self.need_depth = False
        self.last_Balance = '----'
        self.last_amount = '----'
        self.last_account = '----'
        
        self.websocket_mode = None
        self.ping = None 
        self.traded_times_dict = {}
        self.delta_list = {}
        self.delta_cg_list = {}
        self.traded_amount = 0
        self.error_times = 0
        self.error_wait = 0
        self.duibi_price = {'buy':False,
                            'sale':False,
                            'count_times':0}
        
    def get_ticker(self):
        #获取市场行情
        if self.name == 'Zaif':
            #为了处理zaif的nounce问题，我们等一秒: 
            self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp )
        this_Ticker = self.exchange.GetTicker()
        #if random.random() * 100 <50:
        if is_emutest_mode() or random.random() * 100 < 50:
            if self.buy_1*0.8 > this_Ticker['Sell']:
                assert False
                Log('买一价严重低于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)
            elif self.buy_1*1.3 < this_Ticker['Buy']:
                assert False
                Log('买一价严重高于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)    
            elif self.sale_1*1.1 < this_Ticker['Buy']:
                assert False
                Log('卖一价严重高于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)
            elif self.sale_1*0.7 > this_Ticker['Buy']:
                assert False
                Log('卖一价严重低于上一次，估计服务器又出问题了：：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)
            else:    
                #Log('this',this_Ticker)
                #Log('last',self.Ticker)
                self.Ticker = this_Ticker
                self.buy_1 = this_Ticker['Sell']
                self.sale_1 = this_Ticker['Buy']
        else:
            self.Ticker = this_Ticker
            self.buy_1 = this_Ticker['Sell']
            self.sale_1 = this_Ticker['Buy']

    def get_account(self):
        #获取账户信息
        if self.name == 'Zaif':
            #为了处理zaif的nounce问题，我们等一秒: 
            self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp )
            
        self.error_pos = 0
        self.Balance = '未获取到数据'
        self.amount = '未获取到数据'
        self.can_buy = '未获取到数据'
        self.FrozenBalance = '未获取到数据'
        self.FrozenStocks = '未获取到数据'
        self.error_pos = 1
        
        self.account = self.exchange.GetAccount()
        self.error_pos = 2
        self.error_thing = self.account

        self.Balance = _N( self.account['Balance'] , price_N )
        self.amount = _N( self.account['Stocks'] , amount_N )
        self.FrozenBalance = _N( self.account['FrozenBalance'] , price_N )
        self.FrozenStocks = _N( self.account['FrozenStocks'] , amount_N )
        self.can_buy = _N( ( self.Balance  / self.sale_1 ) , amount_N )
        
        self.account_state = 'Done'
        
        self.error_pos = 3
        
    def get_depth(self):
        #获取深度信息
        if self.name == 'Zaif':
            #为了处理zaif的nounce问题，我们等一秒: 
            self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp )
        self.Depth = self.exchange.GetDepth()
        
    def cleanAT(self):
        #清空账户信息和市场行情信息
        #self.account = None
        #self.Ticker = None 
        self.Depth = None 
        self.ping = 0
        
    def delta_init(self, jys_b ,init_delta ):
        #初始化偏置量
        
        differ = abs(self.Ticker['Last'] - jys_b.Ticker['Last'])
        
        # 最大差价
        # 这个对差价过大的交易所作调整用的，设置为你看到过的交易所间的最大差价。
        #"jubi_yunbi_cheack_and_change":0.00005,
        # 对第一个价格的接受程度
        # 1~100之间。建议10%，波动大的币种可以设定大一些。这个值越大，初始学习周期理论上来说需要的就越小。只发挥一次作用。
        #"delta_delta_U1":65,
        if differ < 0.3* jubi_yunbi_cheack_and_change :
            delta_delta_cg1 = 0.2*delta_delta_U1
        elif differ < 0.7 * jubi_yunbi_cheack_and_change :
            delta_delta_cg1 = 0.5*delta_delta_U1
        else:
            delta_delta_cg1 = delta_delta_U1
        
        self.traded_times_dict[jys_b.name] = 0
        self.delta_list[jys_b.name] = (self.Ticker['Last'] - jys_b.Ticker['Last'])*delta_delta_cg1*0.01
        self.delta_cg_list[jys_b.name] = { 'times':0,
                                           'differ_leiji':0}
    
    def cg_delta(self,b_name,differ):
        # 累计学习差价20次后，根据学习速度调整 delta_list 的值
        # delta_cg_list 是用来存储差价历史的
        #Log(self.delta_cg_list)
        #Log('1.times is', self.delta_cg_list[b_name]['times'],' this_delta is' , self.delta_list[b_name])
        
        self.delta_cg_list[b_name]['differ_leiji'] += differ
        self.delta_cg_list[b_name]['times'] += 1
        
        # 原版这里是 > 20, 这是显然的错误, 修正
        # 修正后跑 qtum/btc, binance, huobipro, okex 的
        # 2018/01/21 00:00:00 到 2018/01/22 23:59:59 的数据, 最后的收益率为
        # 3.22%, 但也有 3.21%, 2.89% 的情况, 原因不明...
        if self.delta_cg_list[b_name]['times'] >= 20:
            if cg_delta_speed == 1:
                last_cg = 0.9998
                this_cg = 0.00019
            elif cg_delta_speed == 2:
                last_cg = 0.9995
                this_cg = 0.00048          
            elif cg_delta_speed == 3:
                last_cg = 0.998
                this_cg = 0.0018
            elif cg_delta_speed == 4:
                last_cg = 0.997
                this_cg = 0.0028            
            
            this_cg_differ = self.delta_cg_list[b_name]['differ_leiji']/20
            self.delta_list[b_name] = self.delta_list[b_name]*last_cg + this_cg_differ * this_cg
            self.delta_cg_list[b_name]['times'] = 0
            self.delta_cg_list[b_name]['differ_leiji'] = 0
        #Log('2.times is', self.delta_cg_list[b_name]['times'],' this_delta is' , self.delta_list[b_name])
        
    def buy(self, price,amount ):
        #按照price得价格和amount的价格买一单
        if amount < BorE:
            Log('这一单小于了可交易的最小单，某个交易所可能不接受',self.name,amount)
        else:
            self.do_check = True
            self.last_Balance = self.Balance
            self.last_account = self.account
            
            price = _N(price, price_N)
            amount = _N(amount, amount_N)
            self.account_state = 'wait_for_refresh'
            #self.account = 'wait_for_refresh'
            #下面两行是调试用的，正式版记得删除
            #if for_test >2000 and for_test < 6000:
            #    Log('开始调试错误信息：')
            #    return 
            
            if self.name == 'Zaif':
                #为了处理zaif的nounce问题，我们等一秒: 
                self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp )
                
            return_buy = self.exchange.Buy( price,amount )
            touch_last_order_timestamp()
            if self.name == 'Zaif':
                #临时解决方案
                self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp ) 
                
            return( return_buy )
        
    def sale(self, price,amount ):
        #按照price得价格和amount的价格卖一单
        if amount < BorE:
            Log('这一单小于了可交易的最小单，某个交易所可能不接受',self.name,amount)
        else:
            self.do_check = True
            self.last_amount = self.amount
            self.last_account = self.account
            
            price = _N(price, price_N) 
            amount = _N(amount, amount_N) 
            self.account_state = 'wait_for_refresh'
            #self.account = 'wait_for_refresh'
            
            if self.name == 'Zaif':
                #为了处理zaif的nounce问题，我们等一秒: 
                self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp )  
                
            return_sale = self.exchange.Sell( price,amount )
            touch_last_order_timestamp()
            if self.name == 'Zaif':
                #临时解决方案
                self.last_time_stamp = make_zaif_nounce_problem( self.last_time_stamp ) 
                
            return ( return_sale )
        
    def make_trade_to(self,jys_b,hua_dian = 0.1):
        #计算本交易所相对于b交易所应该买还是卖，以及该设定的价格。
        a = self 
        b = jys_b
        aTicker = self.Ticker 
        bTicker = jys_b.Ticker 
        a_name = self.name 
        b_name = jys_b.name 
        a_depth = self.Depth
        b_depth = jys_b.Depth
        
        price_alast, price_asell, price_abuy = aTicker['Last'] , aTicker['Buy'] , aTicker['Sell']
        price_blast, price_bsell, price_bbuy = bTicker['Last'] , bTicker['Buy'] , bTicker['Sell']
        
        depth_abuy_am,depth_asell_am = a_depth['Asks'][0]['Amount'] , a_depth['Bids'][0]['Amount']
        depth_bbuy_am,depth_bsell_am = b_depth['Asks'][0]['Amount'] , b_depth['Bids'][0]['Amount']
        
        #Log('am a buy and sell is', depth_abuy_am,depth_asell_am ,'b buy and sell is', depth_bbuy_am , depth_bsell_am )
        
        price_asell,price_bsell = price_asell -hua_dian ,price_bsell-hua_dian
        price_abuy,price_bbuy = price_abuy +hua_dian , price_bbuy +hua_dian
        
        
        differ = price_alast - price_blast
        self.cg_delta(b_name,differ)
        delta = self.delta_list[b_name]
        #delta = 0.0
        output = {}
        # FIXME differ 可能为负数，需要取绝对值
        if differ> jubi_yunbi_cheack_and_change*0.7:
            this_might_kk =_N( (abs(differ)/jubi_yunbi_cheack_and_change + 1)*taoli_cha ,2 )
        else:
            this_might_kk = taoli_cha
            
        if more_than_taolicha:
            
            # a卖b买 费用
            fee_asbb = a.Fee['Sell'] + b.Fee['Buy'] + this_might_kk
            # a买b卖 费用
            fee_abbs = a.Fee['Buy'] + b.Fee['Sell'] + this_might_kk

            acha = price_asell - price_bbuy*( 1+fee_asbb * 1.0 /100 ) - delta 
            bcha = price_bsell - price_abuy*( 1+fee_abbs * 1.0 /100 ) + delta
            
            # acha = price_asell - price_bbuy*(1 + fee_asbb_ratio)) - delta
            # bcha = price_bsell - price_abuy*(1 + fee_abbs_ratio)) + delta
        else:    
            acha = price_asell - price_bbuy*( 1+this_might_kk * 1.0 /100 ) - delta
            bcha = price_bsell - price_abuy*( 1+this_might_kk * 1.0 /100 ) + delta
        
        this_might_kk = max( this_might_kk,taoli_cha )
        self.diff_might_k = this_might_kk
        jys_b.diff_might_k = this_might_kk
        
        if acha > 0 :
            output['sale_jys'] = a
            output['sale_jys_name'] = a_name
            output['sales_price'] = price_asell
            output['buy_jys'] = b
            output['buy_jys_name'] = b_name
            output['buy_price'] = price_bbuy
            output['delta'] = delta
            output['jiacha'] = acha
            output['oml'] = min(depth_asell_am,depth_bbuy_am) 
            output['way'] = 'a2b'
            #Log('depth_asell,buy:',depth_asell_am,depth_bbuy_am)

        elif bcha > 0 :
            output['sale_jys'] = b
            output['sale_jys_name'] = b_name
            output['sales_price'] = price_bsell
            output['buy_jys'] = a
            output['buy_jys_name'] = a_name
            output['buy_price'] = price_abuy
            output['delta'] = delta
            output['jiacha'] = bcha
            output['oml'] = min(depth_bsell_am,depth_abuy_am) 
            output['way'] = 'b2a'
            #Log('depth_bsell,buy:',depth_bsell_am,depth_abuy_am)
            
        else:
            output = None
            
        #Log(a_name,acha,b_name,bcha)
        #if output:
            #Log(a_name,b_name,delta)
            #Log('oml is ', output['oml'])

        
        return output
    
    def make_trade_with_amount(self,jys_b,hua_dian = huadian):
        trade_dict = self.make_trade_to(jys_b ,hua_dian = hua_dian)
        
        if not trade_dict:
            return None
        
        sale_jys = trade_dict['sale_jys']
        buy_jys = trade_dict['buy_jys']

        buy_price = trade_dict['buy_price']
        sale_price = trade_dict['sales_price']
        
        buy_jys_stock = buy_jys.account['Stocks']
        sale_jys_stock = sale_jys.account['Stocks'] * 0.99

        sale_jys_balance = sale_jys.account['Balance']
        buy_jys_balance = buy_jys.account['Balance']

        delta = trade_dict['delta']

        this_buyjys_can_buy_stock= buy_jys_balance*1.0 / buy_price * 0.99
        if sale_jys_stock > (buy_jys_stock + BorE)*8:
            Oamount =( sale_jys_stock - buy_jys_stock )*3/5
            #Log("我要放大了，这次一单成交的stock为：",Oamount)
        else:
            #Log('sale price is:',sale_price,'buy price is', buy_price,'delta is', delta)
            this_md = ( sale_price - buy_price - delta)
            xisu = abs(this_md / (abs(delta) + buy_price/beta_rock) )
            Oamount = init_amount * xisu
            
        yuzhi = check_name_and_BorE( trade_dict['sale_jys_name'] ,trade_dict['buy_jys_name'] )
        if Oamount < yuzhi:
            Oamount = yuzhi
        else:
            should_less_is = min(this_buyjys_can_buy_stock,sale_jys_stock,trade_dict['oml'])
            if Oamount > should_less_is:
                Oamount = should_less_is
            
        trade_dict['Oamount'] = _N(Oamount, amount_N)
        trade_dict['should_less_than'] = min( this_buyjys_can_buy_stock , sale_jys_stock , trade_dict['oml'])
        trade_dict['should_less_than_list'] = [ this_buyjys_can_buy_stock , sale_jys_stock , trade_dict['oml'] ]
        return trade_dict

def make_zaif_nounce_problem( last_time_stamp ):
    this_time_stamp = time.time()
    this_time_cha = (this_time_stamp -last_time_stamp )*1000
    
    if this_time_cha < 1001 :
        #sleep_is = _N( 1000 - this_time_cha, 0)
        sleep_is = _N( 1001 - this_time_cha, 0)
        #Log('为了处理zaif的nounce问题，我们等一秒...', _N( sleep_is , 2 ), 'ms  cha_is', this_time_cha )
        Sleep ( sleep_is )
        
    return time.time()
    
def check_name_and_BorE(a_name,b_name):
    if a_name == 'BTCTrade' or b_name == 'BTCTrade':
        return 0.01 
    else:
        return BorE
    
    
import json
listener = {}

class Table():
    """docstring for Table"""
    def __init__(self):
        self.tb = {
            "type" : "table",
            "title" : "Table",
            "cols" : [],
            "rows" : []
        }

    def SetColRow(self, col_index, row_index, row):
        if (type(col_index) is int) and (type(row_index) is int) :
            if (col_index > len(self.tb["cols"])) or (row_index > len(self.tb["rows"])) :
                Log("索引超出范围！col_index:", col_index, "row_index:", row_index)
            else :
                self.tb["rows"][row_index - 1][col_index - 1] = row
        else :
            Log("col_index:", col_index, "row_index:", row_index)
            raise "SetColRow 参数错误!"

    def SetBtn(self, col_index, row_index, cmd, name, callback):
        global listener
        if (type(col_index) is int) and (type(row_index) is int) :
            if (col_index > len(self.tb["cols"])) or (row_index > len(self.tb["rows"])) :
                Log("索引超出范围！col_index:", col_index, "row_index:", row_index)
            else :
                self.tb["rows"][row_index - 1][col_index - 1] = {"type" : "button", "cmd" : cmd, "name" : name}
                listener[cmd] = callback
        else :
            Log("col_index:", col_index, "row_index:", row_index)
            raise "SetColRow 参数错误!"
    
    def SetRows(self, row_index, Rows):
        pass

    def SetCols(self, Cols):
        self.tb["cols"] = Cols

    def GetRows(self, row_index):
        if (type(row_index) is int) and (row_index < len(self.tb["rows"])) :
            return self.tb["rows"][row_index - 1]
        else :
            Log("参数错误！ 或者 参数索引超出范围！")

    def Init(self, title, col_length, row_length):  
        self.tb["title"] = title
        for i in range(1, row_length + 1) :
            if i == 1 :
                for n in range(1, col_length + 1) :
                    self.tb["cols"].append(n)
            self.tb["rows"].append([])
            for m in range(1, col_length + 1) :
                self.tb["rows"][i - 1].append(str(i) + "/" + str(m))


class CreateTableManager():
    """docstring for CreateTableManager"""
    def __init__(self):        # CreateTableManager 构造函数
        self.tables = []       # 用于储存 table 对象
    
    def GetTable(self, index):
        if type(index) is int :
            return self.tables[index]
        elif type(index) is str :
            for i in range(len(self.tables)) :
                if self.tables[i]["title"] == index:
                    return self.tables[i]
        else :
            Log("GetTable参数:", index)
            raise "GetTable 参数错误！"
    
    def AddTable(self, title, col_length, row_length):    # cols, rows
        tb = Table()
        tb.Init(title, col_length, row_length)
        self.tables.append(tb.tb)
        return tb

    def UpdateCMD(self):
        global listener
        cmd = GetCommand()
        if cmd :
            if listener[cmd] :
                listener[cmd](cmd)
            else :
                Log("找不到名为：" + cmd + "的命令")
    
    def LogStatus(self, before, end):
        if is_emutest_mode():
            LogStatus(before)
            draw_table(self.tables)
            LogStatus(end)
        else:
            self.UpdateCMD()
            LogStatus(before + '\n`' + json.dumps(self.tables) + '`\n' + end)

if __name__ == '__main__':
    main()
