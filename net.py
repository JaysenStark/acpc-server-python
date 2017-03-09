import socket
import random
from predefine import READBUF_LEN, NUM_PORT_CREATION_ATTEMPTS



# try opening a socket suitable for connecting to
# if *desiredPort>0, uses specified port, otherwise use a random port
# returns actual port in *desiredPort
# returns 1 for success, or -1 on failure 
def get_listen_socket(listen_port, i, listen_socket):

	desired_port = listen_port[i]

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	if sock == None:
		return -1

	# allow fast socket reuse - ignore failure
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	flag = False # bind success or not
	port = -1

	# bind the socket to the port
	if not desired_port == 0:

		host = 'localhost' #socket.htonl(socket.INADDR_ANY)
		port = desired_port #socket.htons(desired_port)
		addr = (host, port)
		try:
			sock.bind(addr)
		except socket.error:
			return -1

	else:

		host = 'localhost' 
		port = random.randint(1, 64511) % 64512 + 1024
		addr = (host, port)

		t = 0 # counter
		
		while True:
			try:
				sock.bind(addr)
				flag = True
				listen_port[i] = port
				break
			except:
				t += 1
				if t >= NUM_PORT_CREATION_ATTEMPTS:
					break
		# end while loop
	# end if - else

	if not flag:
		return -1

	# listen on the socket
	sock.listen(8)
	listen_socket[i] = sock

	return 1


	
	


	
# get_listener_socket(8001)
