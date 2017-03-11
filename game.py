from predefine import *

action_chars = 'fcr'
suit_chars = 'cdhs'
rank_chars = '23456789TJQKA'


def consume_space(string, consume_equal):
	# string_copy = string[:]
	i = 0
	while string[i] and\
	 (not string[i] == ' ' or (consume_equal and string[i] == '=') ):
		i += 1

	return i

# [unused!]reads up to numItems with scanf format itemFormat from string,
# returning item i in *items[ i ]
# ignore the '=' character if consume_equal is non-zero
# returns the number of characters consumed doing this in charsConsumed
# returns the number of items read 
def read_items(num_items, string):
	
	new_string = string.strip('\n= ')
	tuple = new_string.split(' ')
	assert len(tuple) <= num_items

	if num_items == 1:
		return (1, int(tuple[0]))

	return (len(tuple), list(tuple))
		
	
def read_game(file):

	game = Game()
	stack_read = 4

	for c in range(MAX_ROUNDS):
		game.stack[c] = INT32_MAX

	blind_read = 0
	raise_sizeRead = 0
	game.betting_type = None # todo
	game.num_players = 0
	game.num_rounds = 0
	for c in range(MAX_ROUNDS):
		game.first_player[c] = 1
	for c in range(MAX_ROUNDS):
		game.max_raises[c] = UINT8_MAX
	game.num_suits = 0
	game.num_ranks = 0
	game.num_hole_cards = 0

	for line in file.readlines():

		if line[0] == '#' or line[0] == '\n':
			continue

		if 'end gamedef' == line[:11].lower():

			break

		elif 'gamedef' == line[:7].lower():

			continue

		elif 'stack' == line[:5].lower():

			stack_read, game.stack = read_items(MAX_PLAYERS, line[5:])

		elif 'blind' == line[:5].lower():

			blind_read, game.blind = read_items(MAX_PLAYERS, line[5:])

		elif 'raisesize' == line[:9].lower():

			raise_read, game.raise_size = read_items(MAX_PLAYERS, line[9:])

		elif 'limit' == line[:5].lower():

			game.betting_type = betting_type.limitBetting

		elif 'nolimit' == line[:7].lower():

			game.betting_type = betting_type.noLimitBetting

		elif 'numplayers' == line[:10].lower():

			unused, game.num_players = read_items(1, line[10:])

		elif 'numrounds' == line[:9].lower():

			unused, game.num_rounds = read_items(1, line[9:])

		elif 'firstplayer' == line[:11].lower():

			unused, game.first_player = read_items(MAX_ROUNDS, line[11:])

		elif 'maxraises' == line[:9].lower():

			unused, game.max_raises = read_items(MAX_ROUNDS, line[9:])

		elif 'numsuits' == line[:8].lower():

			unused, game.num_suits = read_items(1, line[8:])

		elif 'numranks' == line[:8].lower():

			unused, game.num_ranks = read_items(1, line[8:])

		elif 'numholecards' == line[:12].lower():

			unused, game.num_hole_cards = read_items(1, line[12:])

		elif 'numboardcards' == line[:13].lower():

			unused, game.num_board_cards = read_items(MAX_ROUNDS, line[13:])

	# end for loop

	# do sanity checks
	if game.num_rounds == 0 or game.num_rounds > MAX_ROUNDS:
		print("invalid number of rounds: %d" % (game.num_rounds,) )
		del game
		return None;
	# todo

	return game


def print_game(file, game):
	pass

def bc_start(game, round):

	start = 0
	for r in range(round):

		start += game.num_board_cards[r]

	return start

def sum_board_cards(game, round):

	total = 0
	for r in range(round):
		total += game.num_board_cards[r]

	return total

def next_player(game, state, cur_player):

	n = cur_player

	n = (n + 1) % game.num_players

	while state.player_folded[n] or state.spent[n] >= game.stack[n]:

		n = (n + 1) % game.num_players

	return n

def current_player(game, state):

	if state.num_actions[state.round]:

		return next_player(game, state, state.acting_player[state.round][state.num_actions[state.round] - 1])

	return next_player(game, state, game.first_player[state.round] + game.num_players - 1)

def num_raises(state):

	ret = 0
	for i in range(state.num_actions):
		if state.action[state.round][i].type == a_raise:
			ret += 1

	return ret

def num_folded(game, state):

	ret = 0
	for p in range(game.num_players):
		if state.player_folded[p]:
			ret += 1

	return ret

def num_called(game, state):

	ret = 0
	for i in range(state.num_actions[state.round], 0, -1):

		p = state.acting_player[state.round][i - 1]

		if state.action[state.round][i - 1].type == a_raise:
		# player initiated the bet, so they've called it

			if state.spent[p] < game.stack[p]:
				# player is not all-in, so they're still acting
				ret += 1

			return ret

		elif state.spent[p] < game.stack[p]:

			ret += 1

	#d=end for loop
	return ret

def num_all_in(game, state):

	ret = 0

	for p in range(game.num_players):

		if state.spent[p] >= game.stack[p]:
			ret += 1

	return ret

def num_acting_players(game, state):

	ret = 0

	for p in range(game.num_players):

		if state.player_folded[p] == 0 and state.spent[p] < game.stack[p]:

			ret += 1
	# end for loop

	return ret



def init_state(game, hand_id, state):

	state.hand_id = hand_id

	state.max_spent = 0
	for p in range(game.num_players):
		state.spent[p] = game.blind[p]
		state.max_spent = max(game.blind[p], state.max_spent)

	if game.betting_type == betting_type.noLimitBetting:
		# if state.max_spent : we'll have to call the big blind and then raise by that
	 	# amount, so the minimum raise-to is 2*maximum blinds
	 	# else :  need to bet at least one chip, and there are no blinds/ante
		state.min_no_limit_raise_to = 2 * state.max_spent if state.max_spent else 1
	else:
		state.min_no_limit_raise_to = 0

	for p in range(game.num_players):
		state.spent[p] = game.blind[p]
		state.max_spent = max(game.blind[p], state.max_spent)
		state.player_folded[p] = 0

	for r in range(game.num_rounds):
		state.num_actions[r] = 0

	state.round = 0
	state.finished = 0

# shuffle a deck of cards and deal them out, writing the results to state
def deal_cards(game, rng, state):
	
	deck = []

	for s in range(game.num_suits):
		for r in range(game.num_ranks):
			deck.append(make_card(r, s))

	# shuffle
	random.shuffle(deck)

	# deal hole cards
	for p in range(game.num_players):
		for i in range(game.num_hole_cards):
			state.hole_cards[p][i] = deck.pop()

	# deal board cards
	idx = 0
	for r in range(game.num_rounds):
		for i in range(game.num_board_cards):
			state.board_cards[idx] = deck.pop()

def read_card(card):
	pass


def state_finished(state):
	assert not state.finished == None
	return state.finished



def test():

	game = read_game(open('holdem.limit.2p.reverse_blinds.game', 'r'))

	for k in game.__dict__:
		print(k, game.__dict__[k])