#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
import json
import getopt
import base64
from Crypto.Cipher import AES

g_use_python3 = (sys.version_info[0] == 3)
g_logfname = 'symarbit.log'

def encrypt_data(data):
    '''data为字符串'''
    global g_logfname
    logfname = g_logfname[:8]
    a = sorted(logfname)
    b = sorted(logfname, reverse=True)
    data += '\0' * (16 - len(data) % 16)
    obj = AES.new(''.join(a+b).encode(), AES.MODE_CBC, ''.join(b+a).encode())
    return base64.b64encode(obj.encrypt(data.encode()))

def decrypt_data(data):
    '''data为字符串'''
    global g_logfname
    logfname = g_logfname[:8]
    a = sorted(logfname)
    b = sorted(logfname, reverse=True)
    obj = AES.new(''.join(a+b).encode(), AES.MODE_CBC, ''.join(b+a).encode())
    return obj.decrypt(base64.b64decode(data.encode())).decode().rstrip('\0')

def usage(cmd):
    msg = '''\
USAGE
    %s [OPTIONS] {filename}

OPTIONS
    -d
    --decrypt           decrypt instead of encrypt

    -o
    --output filename   output file name
    ''' % cmd
    print(msg)

def parse_optitons(argv):
    cmd = argv[0]
    ret_opts = {}
    ret_args = []

    ret_opts['test'] = False
    ret_opts['decrypt'] = False
    ret_opts['output'] = ''

    try:
        opts, ret_args = getopt.gnu_getopt(argv[1:],
                                           'do:',
                                           ['help', 'test',
                                            'output=',
                                            'decrypt'])
    except getopt.GetoptError as err:
        print(err)
        usage(cmd)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            usage(cmd)
            sys.exit(0)
        elif opt in ('-d', '--decrypt'):
            ret_opts['decrypt'] = True
        elif opt in ('-o', '--output'):
            ret_opts['output'] = arg
        else:
            print('unhandled option:', opt, arg)
            usage(cmd)
            sys.exit(2)

    return ret_opts, ret_args

def main(argv):
    opts, args = parse_optitons(argv)

    if not args:
        usage(argv[0])
        return 2

    decrypt = opts.get('decrypt', False)
    for fname in args:
        with open(fname) as fp:
            data = fp.read()
        if decrypt:
            altd = decrypt_data(data)
        else:
            altd = encrypt_data(data).decode()
        altfname = opts.get('output')
        if altfname:
            if altfname == '-':
                sys.stdout.write(altd)
            else:
                with open(altfname, 'w') as fp:
                    fp.write(altd)
        else:
            sys.stdout.write(altd)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
