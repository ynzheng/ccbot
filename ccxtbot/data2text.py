#!/usr/bin/env python3
# coding: utf-8
from __future__ import print_function
import sys
import glob

import zlib
import base64

name = 'symarbit'
try:
    name = sys.argv[1]
except:
    pass

ifname = glob.glob(name + '.cpython-3*-x86_64-linux-gnu.so')[0]
ofname = name + '.txt'

with open(ifname, 'rb') as fp:
    zdata = zlib.compress(fp.read())

b64text = base64.b64encode(zdata)
wrap=78
length=len(b64text)
with open(ofname, 'wb') as fp:
    idx = 0
    while idx < length:
        fp.write(b64text[idx : idx+wrap] + b'\n')
        idx += wrap
    #fp.write(b64text)
print('GENERATE %s' % ofname)
