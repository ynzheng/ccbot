import time
import random
import json
import copy  

initAccount = None
jys_class_list = []
init_dict = {}
init_delta = 0
banzhuan_cha = 0
last_banzhuan_price = 0
str_frozen_id_jys = ['Quoine', 'Coincheck', 'Zaif', 'Huobi']
#debug用: 
FEE_DIC = {'Sell': 0.25,
           'Buy': 0.25 }

FEE_DIC_OTHER = { 'Bitfinex':{'Sell': 0.2,'Buy': 0.2},
                  'AEX':{'Sell': 0.2,'Buy': 0.2},
                  'Kraken':{'Sell': 0.26,'Buy': 0.26},
                  'HitBTC':{'Sell': 0.1,'Buy': 0.1},
                  'OKCoin_EN':{'Sell': 0.2,'Buy': 0.2},
                 'Binance':{'Sell': 0.1,'Buy': 0.1},
                 'OKEX':{'Sell': 0.2,'Buy': 0.2},
                 'ZB':{'Sell': 0.2,'Buy': 0.2},
                 'Huobi':{'Sell': 0.2,'Buy': 0.2},
                 'BitFlyer':{'Sell': 0.01,'Buy': 0.01},
                'Quoine':{'Sell': 0,'Buy': 0},
                'Coincheck':{'Sell': 0,'Buy': 0},
                'Zaif':{'Sell': -0.01,'Buy': -0.01}}

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

duibi_price = {'buy':False,
               'sale':False,
               'count_times':0}

_CDelay( 2000 ) # 容错重复轮询间隔

qushi_action_save = []


def main():
    global chushi, wait_for_saved, for_test
    if len(exchanges)<2:
        Log(exchanges,'只有不足俩，无法套利')
    else:
        this_compare_dict = {} #比较用的字典
        for this_exchange in exchanges:
            jys = JYS(this_exchange)
            if first_use_saved_chushi:
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
            
            Log('当前的',jys.name,'的is_websocket为：',jys.websocket_mode )
            
            jys_class_list.append(jys)
            this_money = jys.account['Balance'] + jys.account['FrozenBalance']
            this_stock = jys.account['Stocks'] + jys.account['FrozenStocks']
            
            if not use_saved_chushi or first_use_saved_chushi:
                chushi['money'] += this_money
                chushi['bi'] += this_stock
                chushi['zg'] += this_money + this_stock * jys.Ticker['Last']
        if not use_saved_chushi or first_use_saved_chushi:    
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
    cishu = 0
    should_show = 0
    this_force_yingli_m2 = 0
    last_1000_jy_amount = 0
    last_1000_jy_amount_cishu = 0
    times_con = 288 * len(jys_class_list)
    #Log(jys_list)
    is_traded_last = 0 
    quary_more = One_more_learns
    TableManager,  table_1, table_2 = create_the_table( jys_class_list , jys_compare_list )
    #LogProfitReset(1) # 用来清空图
    while(1):
        # 中间的仅作测试用，正式版请注释掉
        for_test = cishu
        # 中间的仅作测试用，正式版请注释掉
        this_loop_time = time.time()
        this_time_cha = this_loop_time - last_loop_time
        last_loop_time = this_loop_time
        if this_time_cha*1000 > 0 and this_time_cha *1000< LoopInterval:
            Sleep(LoopInterval)
        
        more_sleep = False
        should_show += 1
        cishu += 1
        last_1000_jy_amount_cishu += 1
        
        make_data_saved( wait_for_saved, chushi, jys_compare_list, banzhuan_cha) #这个函数用来储存信息
        
        for this_jys in jys_class_list:
            
            if is_meet_error_wait:
                #是否需要监测错误单？
                after_trade_do_check( this_jys )
                if this_jys.error_wait >0:
                    this_jys.error_wait -= 1
                    if jys.error_wait %99 == 1:
                        Log('由于之前', jys.name, '出现了错误,这个交易所将在：',jys.error_wait +1 ,'次轮询后再参与交易。')
                    
            if cishu% 37 == 1:
                this_jys.account_state = 'wait_for_refresh_rd'        
                
        try:
        #if 1:
            if cishu % 99 == 1:
                is_traded_last = del_with_frozen(jys_class_list, now_mb, easy_qushi,chushi )
        except:
            pass        
        
        
        if cishu > duibi_times_con + One_more_learns:
            #Log('趋势机启动中')
            #if 1:
            try:
                bucang(jys_class_list , now_mb , chushi, cishu, easy_qushi)
            except:
                pass
            
        clean_data(jys_class_list)
        get_data(jys_class_list, jys_compare_list, cishu)
        
        all_trade_dict = make_trade_dict(jys_compare_list)

        if last_1000_jy_amount_cishu > times_con:
            #每times_con次轮询检查一次当前是否应该调优taolicha
            last_1000_jy_amount, last_1000_jy_amount_cishu = auto_change_taolicha(last_1000_jy_amount, last_1000_jy_amount_cishu) #这个用来自动控制套利差的当前值
        
        if len(all_trade_dict)>0 and cishu > quary_more :
                        
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
                            last_done_amount = last_done_amount - this_trade_Oamount
                            
                            last_1000_jy_amount += this_trade_Oamount
                            is_traded_last = 30

                except:
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
        this_wait_for_saved['saved_jys_first_state'][i[1].name]['traded_amount'] = i[1].traded_amount
        this_wait_for_saved['saved_delta'][i[0].name][i[1].name]['traded_times'] = i[0].traded_times_dict[i[1].name]
    
    this_saved_name1 = saved_name + '1' 
    this_saved_name2 = saved_name + '2'
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
    global taoli_cha
    #这个函数用来控制阈值自动行动
    if taoli_cha < taoli_cha_min:
        taoli_cha = taoli_cha_min
    elif taoli_cha > taoli_cha_max:
        taoli_cha = taoli_cha_max 
    elif last_1000_jy_amount > init_amount * 25 and last_1000_jy_amount < init_amount * 50:
        return last_1000_jy_amount ,last_1000_jy_amount_cishu
    else:
        if last_1000_jy_amount < init_amount :
            taoli_cha -= 0.004
        elif last_1000_jy_amount < init_amount * 20:
            taoli_cha -= 0.001
        elif last_1000_jy_amount > init_amount * 100:
            taoli_cha += 0.015
        elif last_1000_jy_amount > init_amount * 50:
            taoli_cha += 0.002
            
        Log('检测到定位时间内搬砖单数为:',last_1000_jy_amount,"；启动阈值更新，更新后的阈值为:",taoli_cha)
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
    
    for jys in jys_list:
        try:
            duibi_price['buy'] = duibi_price['buy'] * 0.5 + jys.Ticker['Buy'] * 0.5
            duibi_price['sale'] = duibi_price['sale'] * 0.5 + jys.Ticker['Sell'] * 0.5
            
            jys.duibi_price['buy'] = jys.duibi_price['buy'] * 0.5 + jys.Ticker['Buy'] * 0.5
            jys.duibi_price['sale'] = jys.duibi_price['sale'] * 0.5 + jys.Ticker['Sell'] * 0.5 
            
        except:
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
                Log( this_jysname,':获取account数据失败---acc_error_pos:',i.error_pos)
                
        elif  i.account_state == 'wait_for_refresh_rd' :
            rd_time = 20
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
            pass
            #Log('this_jysname',this_jysname,':',error_pos)
    try:       
        does_he_need_depth(jys_compare_list)
    except:
        pass
        #Log('检测是否需要获取深度信息时发生错误')
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
    all_fbalance = 0
    all_fstock = 0
    buy_dict = {}
    sale_dict = {}
    for jys in jys_class_list:
        this_jysname = jys.name
        this_cansale_price = jys.Ticker['Buy']
        this_cansale_amount = jys.account['Stocks']
        this_canbuy_price = jys.Ticker['Sell']
        this_canbuy_stock = jys.account['Balance'] / this_canbuy_price *0.999 
        all_fbalance += jys.account['FrozenBalance']
        all_fstock += jys.account['FrozenStocks']
        
        used_sale_price = jys.duibi_price['sale']
        used_buy_price = jys.duibi_price['buy']
        
        salep_list = {}
        buyp_list = {}
        try:
            if salep_list['amount']  < this_cansale_amount and used_sale_price < this_cansale_price:
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
    
    if all_fstock < 0.1 * now_mb['bi'] and now_mb['bi'] < (1.0 + qushi_sp *1.0/100) * ping_amount:
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
            this_amount = min( this_amount, ping_amount - now_mb['bi'] )
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
            this_amount = min( this_amount, now_mb['bi'] - ping_amount )
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
            buy_jys.error_times += 1
            buy_jys.error_times = min( 5, buy_jys.error_times )
            buy_jys.error_wait = meet_error_wait* buy_jys.error_times
            Log( buy_jys.name, '出错了，接下来它暂时不参与交易')
            
        duibi_price['buy'] = duibi_price['buy'] * 0.8 + buy_price * 0.2
        buy_jys.traded_amount += Oamount 
        try:
            this_sale_id = sale_jys.sale( sale_price , Oamount )
        except:
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
        
        this_fee = ( sale_price*sale_jys.Fee['Sell'] + buy_price*buy_jys.Fee['Buy'] )*Oamount/100
        last_banzhuan_price = (sale_price - buy_price )*Oamount - this_fee
            
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
            
        try:
            Log('A', self.name,'type:', type(self.name))
            self.name = self.name.decode(encoding="utf-8")
        except:
            Log('B', self.name, 'type: str' )
            self.name = str( self.name )
        self.name = str( self.name )
        
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
            self.Fee = FEE_DIC_OTHER[self.name]
        except:
            self.Fee = FEE_DIC
        self.account_state = 'wait_for_refresh'
        self.first_Balance = self.account['Balance'] 
        self.first_amount = self.account['Stocks']
        self.first_price = self.Ticker['Last']
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
        
        this_Ticker = self.exchange.GetTicker()
        self.last_time_stamp = make_zaif_nounce_problem( self.name, self.last_time_stamp )
        
        if random.random() * 100 <50:
            if self.buy_1*0.8 > this_Ticker['Sell']:
                Log('买一价严重低于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)
            elif self.buy_1*1.3 < this_Ticker['Buy']:
                Log('买一价严重高于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)    
            elif self.sale_1*1.1 < this_Ticker['Buy']:
                Log('卖一价严重高于上一次，估计服务器又出问题了：',self.name)
                Log(this_Ticker)
                Log(self.Ticker)
            elif self.sale_1*0.7 > this_Ticker['Buy']:
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
            
        self.error_pos = 0
        self.Balance = '未获取到数据'
        self.amount = '未获取到数据'
        self.can_buy = '未获取到数据'
        self.FrozenBalance = '未获取到数据'
        self.FrozenStocks = '未获取到数据'
        self.error_pos = 1
        
        self.account = self.exchange.GetAccount()
        self.last_time_stamp = make_zaif_nounce_problem( self.name, self.last_time_stamp )
        
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
        self.Depth = self.exchange.GetDepth()
        self.last_time_stamp = make_zaif_nounce_problem( self.name, self.last_time_stamp )
        
    def cleanAT(self):
        #清空账户信息和市场行情信息
        #self.account = None
        #self.Ticker = None 
        self.Depth = None 
        self.ping = 0
        
    def delta_init(self, jys_b ,init_delta ):
        #初始化偏置量
        
        differ = abs(self.Ticker['Last'] - jys_b.Ticker['Last'])
        
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
        #Log(self.delta_cg_list)
        #Log('1.times is', self.delta_cg_list[b_name]['times'],' this_delta is' , self.delta_list[b_name])
        
        self.delta_cg_list[b_name]['differ_leiji'] += differ
        self.delta_cg_list[b_name]['times'] += 1
        
        if self.delta_cg_list[b_name]['times'] > 20:
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
            
            return_buy = self.exchange.Buy( price,amount )
            self.last_time_stamp = make_zaif_nounce_problem( self.name, self.last_time_stamp )  
                
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
                            
            return_sale = self.exchange.Sell( price,amount )
            self.last_time_stamp = make_zaif_nounce_problem( self.name, self.last_time_stamp )      
            
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
        output = {}
        if differ> jubi_yunbi_cheack_and_change*0.7:
            this_might_kk =_N( (abs(differ)/jubi_yunbi_cheack_and_change + 1)*taoli_cha ,2 )
        else:
            this_might_kk = taoli_cha
            
        if more_than_taolicha:
            
            fee_asbb = a.Fee['Sell'] + b.Fee['Buy'] + this_might_kk
            fee_abbs = a.Fee['Buy'] + b.Fee['Sell'] + this_might_kk

            acha = price_asell - price_bbuy*( 1+fee_asbb * 1.0 /100 ) - delta 
            bcha = price_bsell - price_abuy*( 1+fee_abbs * 1.0 /100 ) + delta
            
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

def make_zaif_nounce_problem( jys_name, last_time_stamp ):
    this_time_stamp = time.time()
    this_time_cha = (this_time_stamp -last_time_stamp )*1000
    
    more_wait_list = ['Zaif','Quoine']
    if this_time_cha < 1001 and jys_name in more_wait_list:
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
        self.UpdateCMD()
        LogStatus(before + '\n`' + json.dumps(self.tables) + '`\n' + end)