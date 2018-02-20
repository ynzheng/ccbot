#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import time
import copy

g_use_python3 = (sys.version_info[0] == 3)

def main(argv):
    cfg0 = {
        '__isStock': True,      # 画K线图的时候这个属性才有用
        'title': {
            'text': '差价图',   # 图标题
        },
        'subtitle': {
            'text': '子标题'
        },
        'tooltip': {
            'xDateFormat:': '%Y/%m/%d %H:%M:%S %A',
        },
        'legend': {
            'enabled': True,
        },
        'xAxis': {
            'type': 'datetime',
        },
        'yAxis': {
            'title': {
                'text': '价格',
            },
            'opposite': True,   # False 表示在左边显示，默认值为 True
        },
        # 数据系列，该属性保存的是 各个 数据系列（线， K线图， 标签等..）
        'series': [
            #  索引为0， data 数组内存放的是该索引系列的 数据
            {
                'name': "line1",
                'id': "线1,buy1Price",
                'showInLegend': True,
                'data': []
            },
            # 索引为1，设置了dashStyle: 'shortdash' 即：设置 虚线。
            {
                'name': "line2",
                'id': "线2,lastPrice",
                'dashStyle': 'shortdash',
                'showInLegend': True,
                'data': []
            },
        ]
    }

    now = time.time()
    cfg1 = copy.deepcopy(cfg0)
    charts = [cfg0, cfg1]
    chart = Chart(charts)
    chart.reset()
    for i in range(100):
        chart.add(0, [(now+i)*1000, i])
        chart.add(1, [(now+i)*1000, i+int(100/3)])
        chart.add(2, [(now+i)*1000, i+4])
        chart.add(3, [(now+i)*1000, i+int(100/4)])
    chart.update(charts)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
