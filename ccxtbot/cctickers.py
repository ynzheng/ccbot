#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import time
import subprocess

g_use_python3 = (sys.version_info[0] == 3)
g_running = True

def main(argv):
    exchanges = [
        #'okex',
        #'huobipro',
        #'binance',
        'zb',
        #'quoinex',
        #'poloniex',
        #'hitbtc',
    ]
    symbol = 'ETH/BTC'

    processes = []
    process_cmds = []
    for exchange in exchanges:
        cmd = ['python.exe', 'ccticker_collector.py']
        cmd += [exchange]
        cmd += [symbol]
        cmd += ['--print_interval', '1']
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        processes.append(p)
        process_cmds.append(' '.join(cmd))

    loop_interval_ms = 1000
    loop_count = 0
    prev_loop_time = 0.0
    while g_running:
        loop_count += 1
        curr_loop_time = time.time()
        loop_time_diff_ms = (curr_loop_time - prev_loop_time) * 1000.0
        if loop_time_diff_ms < loop_interval_ms:
            time.sleep((loop_interval_ms - loop_time_diff_ms) / 1000.0)
        prev_loop_time = time.time()

        for i, p in enumerate(processes):
            if not p.poll() is None:
                print(p.communicate()[0])
                print('ERROR %d: %s' % (p.poll(), process_cmds[i]))
                processes.pop(i)
                process_cmds.pop(i)
                continue
            # FIXME
            print(p.stdout.readline(256), end='')

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
