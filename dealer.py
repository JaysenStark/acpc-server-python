import sys
import getopt
import random
import time
import select

from game import read_game
from predefine import *
from net import *
from rng import init_genrand, Rng_state_t

DEFAULT_MAX_INVALID_ACTIONS = UINT32_MAX # todo
DEFAULT_MAX_RESPONSE_MICROS = 600000000
DEFAULT_MAX_USED_HAND_MICROS = 600000000
DEFAULT_MAX_USED_PER_HAND_MICROS = 7000000

class ErrorInfo():
	def __init__(self, max_invalid_actions, max_response_micros, max_used_hand_micros, max_used_macth_micros):
		self.max_invalid_actions = max_invalid_actions
		self.max_response_micros = max_response_micros
		self.max_used_hand_micros = max_used_hand_micros
		self.max_used_macth_micros = max_used_macth_micros

		self.num_invalid_actions = [0 for x in range(MAX_PLAYERS)]
		self.used_hand_micros = [0 for x in range(MAX_PLAYERS)]
		self.used_match_macros = [0 for x in range(MAX_PLAYERS)]
	

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg
		self.usage = \
"\nusage: dealer matchName gameDefFile #Hands rngSeed p1name p2name ... [options]\n\
  -f use fixed dealer button at table\n\
  -l/L disable/enable log file - enabled by default\n\
  -p player1_port,player2_port,... [default is random]\n\
  -q only print errors, warnings, and final value to stderr\n\
  -t/T disable/enable transaction file - disabled by default\n\
  --t_response [milliseconds] maximum time per response\n\
  --t_per_hand [milliseconds] maximum average player time for match\n\
  --start_timeout [milliseconds] maximum time to wait for players to connect\n\
    <0 [default] is no timeout\n" 

def scan_port_string(string, listen_port):

	new_string = string.strip()
	port_tuple = string.split(',')

	if len(port_tuple) > MAX_PLAYERS:
		return -1

	try:

		for i in range(len(port_tuple)):
			listen_port[i] = int(port_tuple[i])

	except ValueError:

		return -1

	return 0

def print_initial_message(match_name, game_name, num_hands, seed, info, log_file):
	line = "# name/game/hands/seed %s %s %d %d\n#--t_response %d\n#--t_hand %d\n#--t_per_hand %d\n"\
	 % (match_name, game_name, num_hands, seed,\
	  info.max_response_micros / 1000,\
	  info.max_used_hand_micros / 1000,\
	  info.max_used_macth_micros / num_hands / 1000)

	print(line)

	# the following kind of check is not important in Python
	if len(line) > MAX_LINE_LEN:

		sys.stderr.write("ERROR: initial game comment too long\n")
		sys.stderr.write("%s" % line)

		if log_file:

			pass

# returns >= 0 if match should continue, -1 on failure
def check_version(seat, read_buff, seat_FD):

	# assert type(seat) == int
	# print("in check version type of read_buff[seat]", type(read_buff[seat]))
	ret = get_line(read_buff, seat_FD, seat, MAX_LINE_LEN, -1)

	if ret < 0: 
		# ret is None
		sys.stderr.write( "ERROR: could not read version string from seat %d\n" %(seat + 1))
		return -1

	line = read_buff[seat]

	if line.count(':') == 1 and line.count('.') == 2:

		(major, minor, unused) = line.strip('\n\r').split(':')[1].split('.')
		print((major, minor, unused))

		if (not int(major) == VERSION_MAJOR) or (int(minor) > VERSION_MINOR):

			sys.stderr.write("ERROR: this server is currently using version %d.%d.%d\n" %\
				 (VERSION_MAJOR, VERSION_MINOR, VERSION_REVISION))
			return -1

	else: 
		# format error
		sys.stderr.write("ERROR: invalid version string %s\n" % line)
		return -1

	return 0




def game_loop(game, seat_name, num_hands, quiet, fixed_seats, rng,\
	 error_info, seat_FD, read_buff, log_file, transaction_file):
	
	# print("in game loop type of read_buff", type(read_buff))
	finish_game_loop = False
	state = MatchState()

	value = [0 for i in range(MAX_PLAYERS)]
	total_value = [0 for i in range(MAX_PLAYERS)]

	# check version string for each player
	for seat in range(game.num_players):
		print("in game loop type of read_buff[seat]", type(read_buff[seat]))
		if check_version(seat, read_buff, seat_FD) < 0:

			return -1
	# end for loop

	send_time = time.time()

	if not quiet: # todo format
		sys.stderr.write("STARTED at %d\n" % send_time)

	hand_id = 0

	if check_error_new_hand(game, error_info) < 0:
		sys.stderr.write("ERROR: unexpected game\n")

	init_state(game, hand_id, state.state)

	deal_cards(game, rng, state.state)

	for seat in range(game.num_p):
		total_value[seat] = 0.0

	# seat 0 is player 0 in first game
	player0_seat = 0

	if not transaction_file:
		# todo
		pass

	if hand_id >= num_hands:
		return finish_game_loop(quiet, game, seat_name, total_value, log_file)

	while True:

		while not state_finished(state.state):

			current_p = current_player(game, state.state)

			for seat in range(game.num_players):

				state.viewing_player = seat_to_player(game, player0_seat, seat)

				if send_player_message(game, state, quiet, seat, seat_FD, t) < 0:
					return -1



	return 0


def seat_to_player(game, player0_seat, seat):
	return (seat + game.num_players - player0_seat) % game.num_players

def player_to_seat(game, player0_seat, player):
	return (player + player0_seat) % game.num_players

def send_player_message(game, state, quiet, seat, seat_FD, send_time):
	pass

def read_player_response(game, state, quiet, send_time, error_info, read_buff, action, recv_time):
	pass

def finish_game_loop(quiet, game, seat_name, total_value, log_file):

	if not quiet:

		cur_time = time.time()
		sys.stderr.write("FINISHED at %d" % cur_time)

	# print final message


	log_string = ""
	for seat in range(game.num_players):
		name = seat_name[seat]
		log_string += "%s: %d\n" % (name, total_value[seat])

	print(log_string)
	sys.stderr.write(log_string)

	if log_file:
		log_file.write(log_string)
	
	return 0



def main(argv = None):
	
	listen_socket = [None for x in range(MAX_PLAYERS)]
	fixed_seats, quiet, append = None, None, None
	seat_FD = [None for x in range(MAX_PLAYERS)]
	file, log_file, transaction_file = None, None, None
	read_buff = [None for x in range(MAX_PLAYERS)]
	game, match_name, game_name = None, None, None
	rng = Rng_state_t()

	seat_name = [None for x in range(MAX_PLAYERS)]

	num_hands, seed, max_invalid_actions = None, None, None

	listen_port = [0 for x in range(MAX_PLAYERS)]

	# game error conditions
	max_invalid_actions = DEFAULT_MAX_INVALID_ACTIONS;
	max_response_micros = DEFAULT_MAX_RESPONSE_MICROS;
	max_used_hand_micros = DEFAULT_MAX_USED_HAND_MICROS;
	max_used_per_hand_micros = DEFAULT_MAX_USED_PER_HAND_MICROS;

	# use log file, don't use transaction file
	use_log_file = 1
	use_transaction_file = 0

	# print all messages
	quiet = 0

	# by default, overwrite preexisting log/transaction files
	append = 0

	# players rotate around the table
	fixed_seats = 0

	# no timeout on startup
	start_timeout_micros = -1

	# if can't dynamiclly get command line, use default instead
	if argv is None:
		argv = sys.argv
		if len(argv[1:]) == 0:
			print(Usage('').usage)

	opts, args = None, None
	# parse command line options
	try:
		try:

			opts, args = getopt.getopt(argv[1:], 'flLp:qtTa', ['t_response=', 't_hand=', 't_per_hand=', 'start_timeout='])

			if len(opts) + len(args) == 0:
				return 1

			for op, value in opts:
				# print(op, value)

				if op == '--t_response':

					try:
						max_response_micros *= int(value)
					except ValueError:
						sys.stderr.write('invalid --t_response parameter\n')
						exit(EXIT_FAILURE)

				elif op == '--t_hand':
					
					try:
						max_used_hand_micros = 1000 * int(value)
					except ValueError:
						sys.stderr.write('invalid --t_hand parameter\n')
						exit(EXIT_FAILURE)

				elif op == '--t_per_hand':
					
					try:
						max_used_per_hand_micros = 1000 * int(value)
					except ValueError:
						sys.stderr.write('invalid --t_per_hand parameter\n')
						exit(EXIT_FAILURE)

				elif op == '--start_timeout':
					
					try:
						start_timeout_micros = 1000 * int(value)
					except ValueError:
						sys.stderr.write('invalid --start_timeout parameter\n')
						exit(EXIT_FAILURE)

				elif op == '-f':

					# fix the player seats
					fixed_seats = 1

				elif op == '-l':

					# no log_file
					use_log_file = 0

				elif op == '-L':

					# use log_file
					use_log_file = 1

				elif op == '-p':

					print('-p--------------')
					ret = scan_port_string(value, listen_port)
					if ret < 0:
						sys.stderr.write("invalid port number! error is %s\n" % port_tuple[i])
						exit(EXIT_FAILURE)

				elif op == '-q':

					quiet = 1

				elif op == '-t':

					# no transaction_file
					use_transaction_file = 0

				elif op == '-T':

					# use transaction_file
					use_transaction_file = 1

				elif op == '-a':

					append = 1

				else:
					sys.stderr.write('ERROR: unknown option %s\n' % args)
					exit(EXIT_FAILURE)
			# end for loop

			# now it still has some unprocessed command line parameters
			# for example [match_name/game/hands/seed/seat_names] 

			# number of parameters not enough 
			if len(args) < 4:
				print(Usage('').usage)
				exit(EXIT_FAILURE)

			match_name = args[0]

			# get game definition
			game_name = args[1]
			file = open(game_name, 'r')
			game = read_game(file)
			if game == None:
				sys.stderr.write("ERROR: could not read game %s\n" % args[1])
				exit(EXIT_FAILURE)

			# get hands numbers
			try:
				num_hands = int(args[2])
				if num_hands <= 0:
					raise ValueError
			except ValueError:
				sys.stderr.write("ERROR: invalid number of hands %s\n" % args[2])
				exit(EXIT_FAILURE)

			# get random number seed
			try:
				seed = int(args[3])
				# print('seed=', seed)

			except ValueError:
				sys.stderr.write("ERROR: invalid number of hands %s\n" % args[2])
				exit(EXIT_FAILURE)

			# get seat names
			if not(len(args) == game.num_players + 4):
				print(Usage('').usage)
				exit(EXIT_FAILURE)

			# save seat names
			for i in range(game.num_players):
				seat_name[i] = args[i+4]

			# seed will be used for random port selection
			init_genrand(rng, seed)
			# print("seed=", seed)
			random.seed(seed)

		except getopt.error as error:
			raise Usage(error.msg)

	except Usage as error:

		sys.stderr.write(error.msg + '\n')
		exit(EXIT_FAILURE)

	# create/open the log
	if use_log_file:

		log_file = open(match_name, 'a+') if append else open(match_name, 'w')

		if not log_file:

			sys.stderr.write("ERROR: could not open log file %s\n" % match_name)
			exit(EXIT_FAILURE)

	else:

		log_file = None

	# create/open the transaction log
	if use_transaction_file:

		transaction_file = open(match_name, 'a+') if append else open(match_name, 'w')

		if not transaction_file:

			sys.stderr.write("ERROR: could not open log file %s\n" % match_name)
			exit(EXIT_FAILURE)

	else:

		transaction_file = None

	# init error_info
	error_info = ErrorInfo(max_invalid_actions, max_response_micros, max_used_hand_micros,\
	 max_used_per_hand_micros * num_hands)

	# print("before:", [listen_port[i] for i in range(game.num_players)])	

	# open sockets for players to listen to
	for i in range(game.num_players):
		
		ret = get_listen_socket(listen_port, i, listen_socket)

		if ret < 0:

			sys.stderr.write("ERROR: could not create listen socket for player %d\n")


	# display socket ports assignment
	for i in range(game.num_players):

		sys.stdout.write(str(listen_port[i]) + ' ')

	sys.stdout.write('\n')

	# print out usage information
	print_initial_message(match_name, game_name, num_hands, seed, error_info, log_file)
		
	# wait for each players to connnect, default no timeout if start_timeout parameter is not given by 
	# command line
	# if no timeout, then accept() will block until all the version data each with an agent are received  
	start_time = time.time()
	
	for i in range(game.num_players):

		print('round:', i)

		if start_timeout_micros >= 0:

			new_time = time.time()
			start_time_left = start_timeout_micros - (new_time - start_time) * 1000000
			if start_time_left < 0:
				start_time_left = 0

			start_time_left_in_sec = start_time_left / 1000000
			print('start_time_left', start_time_left)

			readable, writeable, error = select.select([listen_socket[i]], [], [],\
			 start_time_left_in_sec)
			print(type(readable), len(readable))
			if len(readable) == 0:
				sys.stderr.write("could not get response from seat %d\n" % (i + 1))
				exit(EXIT_FAILURE)
			print(readable)
		# end if start_timeout_micros >= 0

		seat_FD[i], addr = listen_socket[i].accept()
		seat_FD[i].setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		# create readBuff[i] for seat[i] but different from original code
		read_buff[i] = []
		
		# close(listen_socket[i])
		print("%d-th connection established!" % (i + 1))
	# end for loop

	if game_loop(game, seat_name, num_hands, quiet, fixed_seats, rng, error_info,\
		seat_FD, read_buff, log_file, transaction_file) < 0:

		exit(EXIT_FAILURE)

	# some flush job
	#sys.stderr.flush()
	del game

	return exit(EXIT_SUCCESS)


if __name__ == "__main__":
	sys.exit(main())
	# print(help(getopt))

