#!/bin/bash
set -e

if [ -e symarbit.cpython-3*-x86_64-linux-gnu.so ]; then
    srcmt=$(stat -c %Y symarbit.py)
    dllmt=$(stat -c %Y symarbit.cpython-3*-x86_64-linux-gnu.so)
    if [ $srcmt -gt $dllmt ]; then
        ./cysetup.sh
    fi
else
    ./cysetup.sh
fi

./data2text.py

ofile=bvscode.py

cat > "$ofile" << EOF
# botvs@0631ee4378932c71f68c6cb3999eb18d
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time
import base64
import zlib
import rsa

data = '''
EOF

cat symarbit.txt >> "$ofile"
cat >> "$ofile" << EOF
'''

def genkey():
    from rsa import PublicKey, PrivateKey
    b64pubk = b'UHVibGljS2V5KDk5MzQzMTY5NDM4MzgzOTEwOTY2NjYwNTU3MDEzNzIzMzIwNTQ1MjI1MzI4MDc3MzQ5MTA3MzgzNDIyOTE3MjE0OTQ0NTM5MDY3ODA5MTkyMjE3MzcyMjU0NTUzMDgzNTA4MzI3MjI5NDgwMzI3NTY5NDkzMDMzMTk2ODA3MTMwNTQwMTg1MjQ5NDc2MTg3MzEyMjc2MDEzMzEsIDY1NTM3KQ=='
    pubk = eval(base64.b64decode(b64pubk))
    msg = str(int(time.time())).encode()
    enmsg = rsa.encrypt(msg, pubk)
    return enmsg

def main(argv=None):
    global data
    fname = 'symarbit.so'
    zdata = base64.b64decode(data.replace('\n', ''))
    rdata = zlib.decompress(zdata)
    try:
        with open(fname, 'wb') as fp:
            fp.write(rdata)
    except:
        Log('Runtime Error')
        return -1
    import symarbit as m
    os.remove(fname)
    m.run(genkey(), globals())

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
EOF
echo "GENERATE: $ofile"
