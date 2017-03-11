import socket, select
import random
import time

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


def get_line(read_buff, seat_FD, seat, max_len, timeout_micros):

	# print("in get line type of read_buff[seat]", type(read_buff[seat]))
	start, cur_time = -1, -1

	max_len -= 1
	if max_len < 0:
		return -1

	# read the line
	have_start_time = 0
	length = 0

	while length < max_len:

		if len(read_buff[seat]) == 0:
		# buffer is empty

			if timeout_micros >= 0:

				time_left = timeout_micros

				if have_start_time:

					cur_time = time.time()
					time_left -= (cur_time - start) * 1000000

					if time_left < 0:

						time_left = 0

				else:
					# have_start_time = 0
					have_start_time = 1
					start = time.time()

				time_left_in_sec = time_left / 1000000

				readable, writeable, error = select.select([seat_FD[seat]], [], [], time_left_in_sec)

				if len(readable) == 0:

					return -1

			data = seat_FD[seat].recv(4096)
			decoded_data = data.decode()

			print("in get line, receive data from seat %d: %s" % (seat + 1, decoded_data))

			if decoded_data[-1] == '\n':
				read_buff[seat] = decoded_data
				return 0
			else:
				print('unexpected error! ends with not \\n\n')
				return -1



			




	


	
# get_listener_socket(8001)
