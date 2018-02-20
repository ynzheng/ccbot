#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
import emutest
import strategy2
import json
import copy
from strategy2 import *
'''
myex._make_trade_comp_exchange
make_trade_comp_exchange
_make_close_arbit_reverse_order_pair
_make_close_arbit_reverse_order_pair_
caculate_position_offset
'''

class TestEmutest(unittest.TestCase):
    def setUp(self):
        self.backup = emutest.g_unittest

    def tearDown(self):
        emutest.g_unittest = self.backup

    def test_01(self):
        self.assertFalse(emutest.g_unittest)
        emutest.g_unittest = True
        self.assertTrue(emutest.g_unittest)

class TestMain(unittest.TestCase):
    def setUp(self):
        emutest.g_unittest = True
        self.backup = emutest.exchanges[:]
    def tearDown(self):
        emutest.exchanges[1:] = self.backup[1:]
        emutest.g_unittest = False
    def test_main(self):
        del emutest.exchanges[1:]
        self.assertEqual(main(), -1)
        emutest.exchanges += [1] * 50
        self.assertEqual(main(), -1)

class TestNeedUpdateDepth(unittest.TestCase):
    def setUp(self):
        self.bak_g_unittest = emutest.g_unittest
        emutest.g_unittest = True

        self.bak_g_myex_list = g_myex_list[:]
        self.bak_g_arbit_status = copy.deepcopy(g_arbit_status)
        self.bak_g_arbit_stats = copy.deepcopy(g_arbit_stats)
        myex_list = []
        for ex in emutest.exchanges:
            myex_list.append(MyExchange(ex))
            myex_list[-1].fees_mode = MyExchange.FEES_MODE_FORWARD
        self.myex_list = myex_list
    def tearDown(self):
        g_arbit_status.clear()
        g_arbit_status.update(**self.bak_g_arbit_status)
        g_arbit_stats.clear()
        g_arbit_stats.update(**self.bak_g_arbit_stats)
        g_myex_list[:] = self.bak_g_myex_list[:]
        emutest.g_unittest = self.bak_g_unittest

    def test_need_update_depth(self):
        #g_arbit_status.clear()
        #g_arbit_stats.clear()
        #g_all_init_fund['stocks'] = 40.0
        #init_arbit_stats(self.myex_list)
        #myex_comp_list = generate_compare_list(self.myex_list)
        #ret = need_update_depth(self.myex_list, myex_comp_list)
        #print(ret)
        pass

    def test_make_retry_arbit_close_orders(self):
        # 自己撮合的代码
        g_arbit_stats.clear()
        g_arbit_status.clear()
        del g_myex_list[:]
        g_myex_list[:] = self.myex_list
        d = {
            'executed': {
                'buy': {
                    # price 1.1
                    'amount': 1.0,
                    'volume': 1.1,
                },
                'sell': {
                    # price 1.0
                    'amount': 1.5,
                    'volume': 1.5,
                },
                'profit': {
                    'amount': 1.0,
                    'volume': 2.0,
                },
            },
            'canceled': {
                'buy': {
                    # price 1.1
                    'amount': 1.0,
                    'volume': 1.1,
                },
                'sell': {
                    # price 1.0
                    'amount': 1.5,
                    'volume': 1.5,
                },
                'profit': {
                    'amount': 1.0,
                    'volume': 2.0,
                },
            }
        }
        li = ('aa', 'bb', 'cc')
        for a in li:
            g_arbit_status[a] ={}
            dd = g_arbit_status.setdefault(a, {})
            for b in li:
                if a == b:
                    continue
                dd[b] = copy.deepcopy(d)
        g_arbit_stats.update(**copy.deepcopy(g_arbit_status))

        # bb -> aa, cc -> aa
        li_buy = get_canceled_buy_list(self.myex_list, self.myex_list[0])
        li_buy.sort(key=lambda x: x['pair_info']['sell_myex'].name)
        # cc -> aa, cc -> bb
        li_sell = get_canceled_sell_list(self.myex_list, self.myex_list[0])
        li_sell.sort(key=lambda x: x['pair_info']['buy_myex'].name)
        #pjson(li_buy)
        #pjson(li_sell)
        # 'aa'
        ret = make_retry_arbit_close_orders(self.myex_list, self.myex_list[0])
        self.assertEqual(ret, [])
        #pjson(li_buy)
        #pjson(li_sell)
        #pjson(self.myex_list[0].stats)
        self.assertEqual(li_buy[0]['buy']['amount'], 0.0)
        self.assertEqual(li_buy[0]['buy']['volume'], 0.0)
        self.assertEqual(li_sell[0]['sell']['amount'], 0.5)
        self.assertEqual(li_sell[0]['sell']['volume'], 0.5)
        self.assertAlmostEqual(self.myex_list[0].stats['cancel.arbit.profit'],
                               -0.1)

class TestSave(unittest.TestCase):
    def setUp(self):
        emutest.g_unittest = True
        myex_list = []
        for ex in emutest.exchanges:
            ex._set_account(Stocks=20.0, Balance=0.075)
            myex_list.append(MyExchange(ex))
        self.myex_list = myex_list
        self.bak_g_all_init_fund = copy.deepcopy(g_all_init_fund)
        myex_list[0].name = 'binance'
    def tearDown(self):
        emutest.g_unittest = True
        g_all_init_fund.clear()
        g_all_init_fund.update(self.bak_g_all_init_fund)

    def test__load_json_from_file(self):
        fname = '_test.sav'
        data = strategy2._load_json_from_file(fname)
        self.assertEqual(data['myex_list'][0]['name'], 'binance')
        self.assertEqual(data['myex_list'][0]['currency'], 'QTUM_BTC')
        self.assertEqual(data['myex_list'][0]['executed_orders'], {})
        self.assertEqual(data['myex_list'][0]['stats']['order.arbit.buy.count'], 81.0)
        self.assertEqual(data['myex_list'][0]['pending_force']['type'], 'buy')
        self.assertEqual(data['myex_list'][0]['pending_force']['amount'], 0.0)
        self.assertEqual(data['myex_list'][1]['name'], 'huobipro')

        self.assertEqual(data['g_version_info'], [1, 0, 0])
        self.assertEqual(data['g_all_init_fund']['balance'], 0.15)

    def test_make_save_data(self):
        strategy2.g_save_birth_time = ''
        data = make_save_data(self.myex_list)
        self.assertEqual(data['birth_time'], '')

        g_all_init_fund['stocks'] = 0.123456
        data = make_save_data(self.myex_list, birth_time='2012/12/12 12:12:12')
        self.assertEqual(data['myex_list'][1]['name'], 'bb')
        self.assertEqual(data['birth_time'], '2012/12/12 12:12:12')
        self.assertEqual(strategy2.g_save_birth_time, '2012/12/12 12:12:12')
        self.assertEqual(data['g_all_init_fund']['stocks'], 0.123456)

        data = make_save_data(self.myex_list)
        self.assertEqual(data['birth_time'], '2012/12/12 12:12:12')

    def test_load_data_from_file(self):
        strategy2.g_save_birth_time = 'abc'
        g_arbit_status.clear()
        g_arbit_stats.clear()
        fname = '_test.sav'
        load_data_from_file(self.myex_list, fname)
        self.assertEqual(g_arbit_stats['binance']['huobipro']['executed']['sell']['amount'], 293.08)
        self.assertEqual(g_arbit_status['binance']['huobipro']['executed']['profit']['amount'], 292.84314)
        self.assertEqual(self.myex_list[0].stats['order.arbit.buy.count'], 81.0)
        self.assertFalse(self.myex_list[1].stats)
        self.assertEqual(strategy2.g_save_birth_time, 'abc')

class TestArbitStatus(unittest.TestCase):
    def setUp(self):
        self.bak_g_unittest = emutest.g_unittest
        emutest.g_unittest = True
        self.backup = copy.deepcopy(g_arbit_status)
        myex_list = []
        for ex in emutest.exchanges:
            myex_list.append(MyExchange(ex))
        self.myex_list = myex_list
    def tearDown(self):
        g_arbit_status.clear()
        g_arbit_status.update(**self.backup)
        emutest.g_unittest = self.bak_g_unittest

    def test_trim_all_arbit_status(self):
        g_arbit_status.clear()
        d = {
            'executed': {
                'buy': {
                    # price 1.1
                    'amount': 1.0,
                    'volume': 1.1,
                },
                'sell': {
                    # price 1.0
                    'amount': 1.5,
                    'volume': 1.5,
                },
                'profit': {
                    'amount': 1.0,
                    'volume': 2.0,
                },
            },
            'canceled': {
                'buy': {
                    # price 1.1
                    'amount': 1.0,
                    'volume': 1.1,
                },
                'sell': {
                    # price 1.0
                    'amount': 1.5,
                    'volume': 1.5,
                },
                'profit': {
                    'amount': 1.0,
                    'volume': 2.0,
                },
            }
        }
        li = ('aa', 'bb', 'cc')
        for a in li:
            g_arbit_status[a] ={}
            dd = g_arbit_status.setdefault(a, {})
            for b in li:
                if a == b:
                    continue
                dd[b] = copy.deepcopy(d)

        # bb -> aa, cc -> aa
        li_buy = get_canceled_buy_list(self.myex_list, self.myex_list[0])
        li_buy.sort(key=lambda x: x['pair_info']['sell_myex'].name)
        self.assertEqual(g_arbit_status['bb']['aa']['canceled']['buy']['amount'],
                         li_buy[0]['buy']['amount'])
        self.assertEqual(g_arbit_status['bb']['aa']['canceled']['buy']['volume'],
                         li_buy[0]['buy']['volume'])
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['buy']['amount'],
                         li_buy[1]['buy']['amount'])
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['buy']['volume'],
                         li_buy[1]['buy']['volume'])
        # cc -> aa, cc -> bb
        li_sell = get_canceled_sell_list(self.myex_list, self.myex_list[-1])
        li_sell.sort(key=lambda x: x['pair_info']['buy_myex'].name)
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['amount'],
                         li_sell[0]['sell']['amount'])
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['volume'],
                         li_sell[0]['sell']['volume'])
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['amount'],
                         li_sell[1]['sell']['amount'])
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['volume'],
                         li_sell[1]['sell']['volume'])

        #pjson(g_arbit_status)
        trim_all_arbit_status(self.myex_list)
        #pjson(g_arbit_status)
        self.assertEqual(g_arbit_status['bb']['cc']['executed']['buy']['amount'], 0.0)
        self.assertEqual(g_arbit_status['bb']['cc']['executed']['buy']['volume'], 0.0)
        self.assertEqual(g_arbit_status['bb']['cc']['executed']['sell']['amount'], 0.5)
        self.assertEqual(g_arbit_status['bb']['cc']['executed']['sell']['volume'], 0.5)
        self.assertEqual(g_arbit_status['bb']['cc']['executed']['profit']['amount'], 2.0)
        self.assertEqual(g_arbit_status['bb']['aa']['executed']['buy']['amount'], 0.0)
        self.assertEqual(g_arbit_status['bb']['aa']['executed']['buy']['volume'], 0.0)
        self.assertEqual(g_arbit_status['bb']['aa']['executed']['sell']['amount'], 0.5)
        self.assertEqual(g_arbit_status['bb']['aa']['executed']['sell']['volume'], 0.5)
        self.assertEqual(g_arbit_status['bb']['aa']['executed']['profit']['amount'], 2.0)
        # fee 0.25%
        self.assertAlmostEqual(g_arbit_status['bb']['cc']['executed']['profit']['volume'], 1.89475)

        li_buy = get_canceled_buy_list(self.myex_list, self.myex_list[0])
        self.assertFalse(li_buy)
        # cc -> aa, cc -> bb
        li_sell = get_canceled_sell_list(self.myex_list, self.myex_list[-1])
        li_sell.sort(key=lambda x: x['pair_info']['buy_myex'].name)
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['amount'], 0.5)
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['volume'], 0.5)
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['amount'], 0.5)
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['volume'], 0.5)

        reset_all_canceled_status(self.myex_list)
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['amount'], 0.0)
        self.assertEqual(g_arbit_status['cc']['aa']['canceled']['sell']['volume'], 0.0)
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['amount'], 0.0)
        self.assertEqual(g_arbit_status['cc']['bb']['canceled']['sell']['volume'], 0.0)

    def test__trim_arbit_status(self):
        d = {
            'buy': {
                # price 1.1
                'amount': 1.0,
                'volume': 1.1,
            },
            'sell': {
                # price 1.0
                'amount': 1.5,
                'volume': 1.5,
            },
            'profit': {
                'amount': 1.0,
                'volume': 2.0,
            },
        }

        #pjson(d)
        strategy2._trim_arbit_status(d, 0.1, 0.2)
        #pjson(d)
        self.assertEqual(d['buy']['amount'], 0.0)
        self.assertEqual(d['buy']['volume'], 0.0)
        self.assertEqual(d['sell']['amount'], 0.5)
        self.assertEqual(d['sell']['volume'], 0.5)
        self.assertEqual(d['profit']['amount'], 2.0)
        self.assertAlmostEqual(d['profit']['volume'], 2.0 - 0.1032)

class TestBaseFunc(unittest.TestCase):
    def setUp(self):
        emutest.g_unittest = True
        myex_list = []
        for ex in emutest.exchanges:
            ex._set_account(Stocks=20.0, Balance=0.075)
            myex_list.append(MyExchange(ex))
        self.myex_list = myex_list
    def tearDown(self):
        emutest.g_unittest = False

    def test_norm4json(self):
        j = norm4json(self.myex_list)
        self.assertFalse(j in self.myex_list)
        d = {'a': {'b': 'c'}}
        self.assertFalse(norm4json(d) is d)
        self.assertFalse(norm4json(d)['a'] is d['a'])
        self.assertTrue(norm4json(d) == d)

    def test_init(self):
        bak = exchange.account
        exchange.account = None
        with self.assertRaises(AssertionError):
            MyExchange(exchange)
        exchange.account = bak

        bak = exchange.ticker
        exchange.ticker = None
        with self.assertRaises(AssertionError):
            MyExchange(exchange)
        exchange.ticker = bak

    def test_names(self):
        li = ['aa', 'bb', 'cc']
        for idx, myex in enumerate(self.myex_list):
            self.assertEqual(myex.name, li[idx])

    def test_ticker(self):
        for idx, myex in enumerate(self.myex_list):
            myex.botvs_exchange.ticker['High'] = None
            myex.botvs_exchange.ticker['Sell'] = None
            myex.botvs_exchange.ticker['Buy'] = None
            #myex.botvs_exchange.ticker['Last'] = None
            del myex.botvs_exchange.ticker['Last']
            tk = myex.get_ticker()
            for k in ('Sell', 'Buy', 'Last'):
                self.assertEqual(tk[k], 0.0)
            self.assertEqual(tk['High'], None)

    def test_get_account(self):
        for myex in self.myex_list:
            self.assertEqual(myex.get_account()['Balance'], 0.075)
            self.assertEqual(myex.get_account()['FrozenBalance'], 0.0)
            self.assertEqual(myex.get_account()['Stocks'], 20.0)
            self.assertEqual(myex.get_account()['FrozenStocks'], 0.0)

    def test__caculate_position_offset(self):
        from strategy2 import _caculate_position_offset
        self.assertEqual(_caculate_position_offset(0, 1, 1), 100)
        self.assertEqual(_caculate_position_offset(1, 0, 1), -100)
        self.assertEqual(_caculate_position_offset(1, 0, 0), 0)
        self.assertEqual(_caculate_position_offset(0, 0, 0), 0)
        self.assertEqual(_caculate_position_offset(10, 10, 3), -50)
        self.assertEqual(_caculate_position_offset(10, 10, 1), 0)

    def test_seconds_to_loop_count(self):
        self.assertEqual(seconds_to_loop_count(1, 1000), 1)
        self.assertEqual(seconds_to_loop_count(1, 1001), 1)
        self.assertEqual(seconds_to_loop_count(1, 10000), 1)
        self.assertEqual(seconds_to_loop_count(36, 1000), 36)
        self.assertEqual(seconds_to_loop_count(36, 250), 36*4)

def all_setup():
    del emutest.exchanges[1:]
    for idx, name in enumerate(('bb', 'cc')):
        emutest.exchanges.append(emutest.Exchange(name))
    emutest.exchange.name = 'aa'
    assert emutest.exchanges[0].name == 'aa'
    assert emutest.exchange is emutest.exchanges[0]

if __name__ == '__main__':
    all_setup()
    unittest.main()
