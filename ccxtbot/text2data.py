#!/usr/bin/env python
# coding: utf-8

import zlib
import base64

ifname = 'symarbit.txt'
ofname = 'symarbit.cpython-36m-x86_64-linux-gnu.so.2'

with open(ifname, 'r') as fp:
    zdata = base64.b64decode(fp.read().replace('\n', ''))

rdata = zlib.decompress(zdata)
with open(ofname, 'wb') as fp:
    fp.write(rdata)
