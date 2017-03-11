import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('127.0.0.1', 9999))

cnt = 0
for data in [b'Michael', b'Tracy', b'Sarah']:
    s.send(data)
    print(cnt,'t-h')
    cnt+=1
    time.sleep(4)


s.send(b'exit')
s.close()