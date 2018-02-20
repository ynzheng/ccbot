#!/bin/bash
set -e

name=botvsext
ofile=extapp.py

if [ -e $name.cpython-3*-x86_64-linux-gnu.so ]; then
    srcmt=$(stat -c %Y $name.py)
    dllmt=$(stat -c %Y $name.cpython-3*-x86_64-linux-gnu.so)
    if [ $srcmt -gt $dllmt ]; then
        ./cysetup_$name.sh
    fi
else
    ./cysetup_$name.sh
fi

./data2text.py $name

cat > "$ofile" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import time
import base64
import zlib

data = '''
EOF

cat $name.txt >> "$ofile"
cat >> "$ofile" << EOF
'''

def main(argv=None):
    global data
    argv = [] if argv is None else argv
    fname = '$name.so'
    zdata = base64.b64decode(data.replace('\n', ''))
    rdata = zlib.decompress(zdata)
    try:
        with open(fname, 'wb') as fp:
            fp.write(rdata)
    except:
        Log('Runtime Error')
        return -1
    import $name as m
    os.remove(fname)
    m.main(argv)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
EOF
chmod +x "$ofile"
echo "GENERATE: $ofile"
