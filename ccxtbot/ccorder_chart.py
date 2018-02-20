#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import time
import os
import os.path
import gzip
import copy
import json
import getopt

g_use_python3 = (sys.version_info[0] == 3)

def Log(*args):
    print(*args)

def norm_time(strt):
    '''
    2012/12/12 11:12:13 -> 2012-12-12 11-12-13
    转为写记录时的标准时间格式
    '''
    d, t = strt.split()
    d = d.replace('/', '-')
    t = t.replace(':', '-')
    h, m, s = t.split('-')

    im = int(int(int(m) / 10) * 10)
    t = '%s-%02d-%s' % (h, im, '00')
    return d + ' ' + t

def time2norm_time(t):
    '''
    秒 -> 写时的标准时间格式
    '''
    timefmt = '%Y-%m-%d %H-%M-%S'
    tt = time.strftime(timefmt, time.localtime(t))
    return norm_time(tt)

def trim_time(t):
    '''
    秒 -> 裁剪到最近 10 分钟间隔的 秒
    '''
    timefmt = '%Y-%m-%d %H-%M-%S'
    dt = time2norm_time(t)
    return time.mktime(time.strptime(dt, timefmt))

class ExchangeRecords():
    def __init__(self, exchange, symbol, start_time, stop_time, folder='.'):
        '''
        开始时间
        结束时间（包含结束时间）

        开始时间可为整数，例如 int(time.time())，
        也可为字符串，如 2012-12-12 18:00:00，
        如果为整数，即表示从19700101开始的秒数，utc
        如果为字符串，时区为 GMT+8
        '''
        self.timefmt = '%Y-%m-%d %H-%M-%S'
        self.exchange = exchange
        self.symbol = symbol.replace('/', '_').upper()

        if isinstance(start_time, (int, float)):
            self.stime = trim_time(start_time)
        else:
            self.stime = int(time.mktime(time.strptime(norm_time(start_time),
                                                       self.timefmt)))

        if isinstance(stop_time, (int, float)):
            self.etime = trim_time(stop_time)
        else:
            # 要包含结束时间的
            self.etime = int(time.mktime(time.strptime(norm_time(stop_time),
                                                       self.timefmt)))

        self.folder = os.path.abspath(os.path.join(folder, exchange,
                                                   self.symbol))

        self._dt = 0
        self._fp = None
        self._prev_record = []

    def _get_fname(self, t):
        d, t = time2norm_time(t).split(' ')
        return os.path.join(self.folder, d, t + '.txt.gz')

    def get_one_file_raw_records(self):
        '''
        @return     None 表示结束，[] 表示获取失败
        '''
        records = []

        t = self.stime + self._dt
        if t >= self.etime + 600:
            # None 代表结束
            return None

        fname = self._get_fname(t)
        if not self._fp or self._fp.name != fname:
            if self._fp:
                self._fp.close()
            try:
                self._fp = gzip.open(fname)
            except IOError as err:
                print(err.message)
                print(err.strerror)
                self._fp = None
                self._dt += 600
                return []

        for line in self._fp.readlines():
            record = line.split()
            records.append(record)
            # 一次读 600 个记录
        self._dt += 600

        return records

    def get_one_raw_record(self):
        record = []

        t = self.stime + self._dt
        if t >= self.etime + 600:
            return None

        fname = self._get_fname(t)
        # 第一次或者满600记录后切换
        if not self._fp or self._fp.name != fname:
            if self._fp:
                self._fp.close()
            try:
                self._fp = gzip.open(fname)
            except IOError as err:
                if self._dt % 600 == 0:
                    print('%s: %s' % (err.strerror, err.filename))
                self._fp = None
                self._dt += 1
                return []

        self._dt += 1
        line = self._fp.readline()
        if not line:
            # 记录少于秒数，提前切换文件
            tt = trim_time(self.stime + (self._dt - 1) + 600)
            if tt >= self.etime + 600:
                return None
            self._dt = tt - self.stime + 1
            self._fp.close()
            fname = self._get_fname(tt)
            try:
                self._fp = gzip.open(fname)
            except IOError as err:
                print('%s: %s' % (err.strerror, err.filename))
                self._fp = None
                return []
            line = self._fp.readline()

        if line:
            li = line.split()
            assert len(li) == 9
            # t ts tz b1 ba s1 sa vwap last
            # 0  1  2  3  4  5  6    7    8
            record = li

        return record


    def get_one_record(self):
        record = self.get_one_raw_record()
        if not record:
            return record

        # t ts tz m1 ma s1 sm vwap last
        t = record[0]
        m1 = record[3]
        s1 = record[5]
        last = record[8]
        result = [t, m1, s1, last]

        return result

    def __del__(self):
        if self._fp:
            self._fp.close()

def usage(cmd):
    msg = '''\
USAGE
    %s [OPTIONS] exchange1 exchange2 ...

OPTIONS
    --start     start time, eg. '2012/12/12 11-12-13'

    --stop      stop time,  eg. '2012/12/12 11-32-13'

    --symbol    eg. qtum/btc

    --folder    folder of data

    --prec      (optional) precision of price, default is 8

    --file      (optional) file to save, default is StockChart,
                always add .html suffix

    -v, --verbose
                more information
    ''' % (cmd,)
    Log(msg)

def parse_options(argv):
    cmd = argv[0]
    ret_opts = {}
    ret_args = []

    oplst = ('start', 'stop', 'symbol', 'folder', 'prec', 'file')
    oplst = list(map(lambda x: '--'+x, oplst))
    try:
        opts, ret_args = getopt.gnu_getopt(argv[1:], 'hv',
                                           ['help',
                                            'start=',
                                            'stop=',
                                            'symbol=',
                                            'folder=',
                                            'prec=',
                                            'file='])
    except getopt.GetoptError as err:
        Log(err)
        usage(cmd)
        sys.exit(2)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage(cmd)
            sys.exit(0)
        elif o in ('-v', '--verbose'):
            ret_opts['verbose'] = True
        elif o == '--start':
            ret_opts['start'] = a
        elif o in oplst:
            ret_opts[o[2:]] = a
        else:
            Log('unhandled option:', o, a)
            usage(cmd)
            sys.exit(2)

    return ret_opts, ret_args

def unittest():
    assert norm_time('2012/12/12 18:19:20') == '2012-12-12 18-10-00'
    assert norm_time('2012-01-08 18-59-59') == '2012-01-08 18-50-00'

    assert time2norm_time(1516613686) == '2018-01-22 17-30-00' # 17-34-46

    # (1516617797.591982, 'Mon Jan 22 18:43:17 2018')
    assert trim_time(1516617797.591982) == 1516617797 - 3*60 - 17 == 1516617600
    inst = ExchangeRecords('a', 'QTUM_BTC', 
                           '2018/1/22 18:43:17',
                           '2018/1/22 18:50:17',
                           'data')
    assert inst.stime == 1516617600
    assert inst.etime == 1516617600 + 600

    inst = ExchangeRecords('binance', 'qtum/btc',
                           '2012/12/12 18:19:20',
                           '2012/12/12 19:59:59',
                           'data')
    assert inst.exchange == 'binance'
    assert inst.symbol == 'QTUM_BTC'

def main(argv):
    from highcharts import Highstock    # 暂时这样避免其他脚本 import 出错
    unittest()

    opts, args = parse_options(argv)
    #exchanges = ('binance', 'huobipro', 'okex', 'zb')
    #symbol = 'qtum/btc'
    #sdt = '2018-01-20 18-00-00'
    #edt = '2018-01-20 18-59-00'
    #folder = r'C:\Users\Eph\Desktop\CC\trade\ccxtbot\CCMarkets\data'
    exchanges = args
    symbol = opts.get('symbol')
    sdt = opts.get('start')
    edt = opts.get('stop')
    folder = opts.get('folder')
    prec = int(opts.get('prec', 8))
    fname = opts.get('file', 'StockChart')
    verbose = opts.get('verbose', False)
    if not exchanges or not symbol or not sdt or not edt or not folder:
        usage(argv[0])
        return 2

    options = {
        'chart': {
            'height': '50%', # default None
        },
        'title': {
            'text': 'Price Difference',
        },
        "tooltip": {
            "xDateFormat": "%Y-%m-%d %H:%M:%S %A",  # NOTE: BUG, 设置不生效
            'pointFormat': '<span style="color:{point.color}">' + '\\u25CF'.decode('unicode-escape') + \
                           '</span> {series.name}: <b>{point.y}</b><br/>',
            'padding': 1,   # default 8
        },
        "legend": {
            "enabled": True
        },
        "xAxis": {
            "type": "datetime"
        },
        'yAxis': {
            'title': {
                'text': '价格',
            },
            'opposite': True,   # False 表示在左边显示，默认值为 True
        },
         # 这是K线图的属性，不画K线图的话不需要
        "plotOptions": {
            "candlestick": {
                "color": "#d75442",
                "upColor": "#6ba583"
            }
        },
        "rangeSelector": {
            "buttons": [
                {
                    "type"  : "hour",
                    "count" : 1,
                    "text"  : "1h",
                },
                {
                    "type"  : 'hour',
                    "count" : 3,
                    "text"  : "3h"
                },
                {
                    "type"  : "hour",
                    "count" : 6,
                    "text"  : "6h"
                },
                {
                    "type"  : "hour",
                    "count" : 12,
                    "text"  : "12h"
                },
                {
                    "type"  : "all",
                    "text"  : "All"
                }
            ],
            #"selected": 2,  # 默认选择的索引号，从0开始，默认值为 undefined
            "inputEnabled": True,
            "inputBoxWidth": 150, # default 90
            'inputDateFormat': '%Y/%m/%d %H:%M:%S',
            'inputEditDateFormat': '%Y/%m/%d %H:%M:%S',
        },
    }

    chart = Highstock()
    chart.set_options('global', {'timezoneOffset': -8 * 60})

    chart.set_dict_options(options)
    #chart.set_options('chart', {'height': None})
    chart.set_options('tooltip', {
        #'pointFormat': '<span style="color:{point.color}">' + '\\u25CF'.decode('unicode-escape') + \
                       #'</span> {series.name}: <b>{point.y:.%df}</b><br/>' % prec,
        'valueDecimals': prec,
        'valueSuffix': ' ' + symbol.replace('/','_').upper().split('_')[1],
    })

    ers = []
    stats = {}
    for exchange in exchanges:
        inst = ExchangeRecords(exchange, symbol, sdt, edt, folder)
        ers.append(inst)
        stats[exchange] = {}
        stats[exchange]['records_count'] = 0

    chart.set_options('subtitle', {'text': ers[0].symbol.replace('_', '/')})

    # 'binance': {'Buy': x, 'Sell': y}
    all_records = {}
    loop_count = 0
    # 标记哪个交易所已经拿完数据了
    # {exchange: True/False, ...}
    ctl = {}
    for inst in ers:
        ctl[inst.exchange] = False

    while True:
        all_true = True
        for v in ctl.itervalues():
            if not v:
                all_true = False
                break
        if ctl and all_true:
            break

        loop_count += 1
        for inst in ers:
            record = inst.get_one_record()
            if record is None:
                ctl[inst.exchange] = True
                continue

            records_dict = all_records.setdefault(inst.exchange, {})
            if not record:
                #ctl[inst.exchange] = True
                continue
            stats[inst.exchange]['records_count'] += 1

            # 不需要小数点
            t = int(int(float(record[0]))*1000)
            #t += 3600*1000*8 # GMT+8
            buy = records_dict.setdefault('buy', [])
            buy.append([t, float(record[1])])
            sell = records_dict.setdefault('sell', [])
            sell.append([t, float(record[2])])
            last = records_dict.setdefault('last', [])
            last.append([t, float(record[3])])

    if verbose:
        print('loop_count:', loop_count)
        Log(json.dumps(stats, indent=4, sort_keys=True))
    for exchange in exchanges:
        records_dict = all_records[exchange]
        chart.add_data_set(records_dict['buy'], series_type='line', name='%s buy' % exchange)
        chart.add_data_set(records_dict['sell'], series_type='line', name='%s sell' % exchange)
        chart.add_data_set(records_dict['last'], series_type='line', name='%s last' % exchange)
    # 后缀名值 .html
    chart.save_file(filename=fname)
    Log('Successfully write to the file:', fname + '.html')

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
