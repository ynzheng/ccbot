#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import json
import time

g_use_python3 = (sys.version_info[0] == 3)

cfg = {
    'title': {
        'text': '差价图',
    },
    "tooltip": {
        "xDateFormat": "%Y-%m-%d %H:%M:%S %A"
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
                "count" : 8,
                "text"  : "8h"
            },
            {
                "type"  : "all",
                "text"  : "All"
            }
        ],
        "selected": 2,
        "inputEnabled": True
    },
    "series": [],

    # 'customize'
    'labelIdx': {},
}

# 设置图表标题
def PlotSubtitle(chart, cfg, subtitle, title=None):
    '''
    title       - 这组图表的标题
    subtitle    - 这个图表的标题，即副标题
    '''
    cfg['subtitle'] = {'text': subtitle}
    if not title is None:
        cfg['title'] = {'text': title}

# 画指标线
def PlotLine(chart, cfg, label, dot, Ntime=None):
    labelIdx = cfg.get('labelIdx', {})
    series = cfg.setdefault('series', [])
    if not label in labelIdx:
        seriesIdx = len(series)
        labelIdx[label] = seriesIdx
        series.append({
            "type": "line",
            "yAxis": 0,
            "showInLegend": True,
            "name": label,
            "data": [],
            "tooltip": {"valueDecimals": 5}
            })
        chart.update(cfg)
    else:
        seriesIdx = labelIdx[label]
    if Ntime is None:
        Ntime = int(time.time() * 1000)
    chart.add(seriesIdx, [Ntime, dot])

def main(argv):
    global cfg
    chart = Chart(cfg)
    while True:
        ticker = exchange.GetTicker()
        if ticker:
            PlotSubtitle(chart, cfg, '%s 差价图' % exchange.GetName())
            PlotLine(chart, cfg, 'High', ticker.High)
            PlotLine(chart, cfg, "Low", ticker.Low)
            PlotLine(chart, cfg, "Buy", ticker.Buy)
            PlotLine(chart, cfg, "Sell", ticker.Sell)
            PlotLine(chart, cfg, 'Last', ticker.Last)
            chart.update(cfg)
        Sleep(60000)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
