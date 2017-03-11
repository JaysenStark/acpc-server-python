import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 9999))
s.listen(5)

print('wait:')


cnt = 0

sock, addr = s.accept()

while True:
	data = sock.recv(1024)
	print(len(data))
	