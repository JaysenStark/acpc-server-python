
# for net.py
READBUF_LEN = 4096
NUM_PORT_CREATION_ATTEMPTS = 10


EXIT_FAILURE = 2
EXIT_SUCCESS = 0

# for game.py
INT32_MAX = 2^31 - 1
UINT8_MAX = 2^8 - 1
UINT32_MAX = 2^32 - 1

VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_REVISION = 0

MAX_ROUNDS = 4
MAX_PLAYERS = 10
MAX_BOARD_CARDS = 7
MAX_HOLE_CARDS = 3
MAX_NUM_ACTIONS = 64
MAX_SUITS = 4
MAX_RANKS = 13
MAX_LINE_LEN = READBUF_LEN

NUM_ACTION_TYPES = 3

from enum import Enum, unique

@unique
class ActionType(Enum):
	a_fold = 0
	a_call = 1
	a_raise = 2
	a_invalid = NUM_ACTION_TYPES # =3

class betting_type(Enum):
	limitBetting = 0
	noLimitBetting = 1
	

class Action():
	def __init__(self):
		self.self.type = None # is action a fold, call, or raise?
		self.size = None # for no-limit raises, we need a size

class Game():
	def __init__(self):
		# stack sizes for each player
		self.stack = list(range(MAX_PLAYERS))

		# entry fee for game, per player
		self.blind = list(range(MAX_PLAYERS))

		# size of fixed raises for limitBetting games
		self.raise_size = list(range(MAX_ROUNDS))

		# general class of game
		self.betting_type = None # todo

		# number of players in the game
		self.num_players = None

		# number of betting rounds
		self.num_rounds = None

		# first player to act in a round
		self.first_player = list(range(MAX_ROUNDS))

		# number of bets/raises that may me made in each round
		self.max_raises = list(range(MAX_ROUNDS))

		# number of suits and ranks in the deck of cards 
		self.num_suits = None
		self.num_ranks = None

		# number of private player cards
		self.num_hole_cards = None

		# number of shared public cards each round
		self.num_board_cards = list(range(MAX_ROUNDS))


class State():
	def __init__(self):
		self.hand_id = None

		# largest bet so far, including all previous rounds
		self.max_spend = None

		# minimum number of chips a player must have spend in total to raise
    	# only used for noLimitBetting games
		self.min_no_limit_raise_to = None

		# spent[ p ] gives the total amount put into the pot by player p
		self.spent = list(range(MAX_PLAYERS))

		# action[ r ][ i ] gives the i'th action in round r
		self.action = [[0 for r in range(MAX_NUM_ACTIONS)] for i in range(MAX_ROUNDS)]

		# actingPlayer[ r ][ i ] gives the player who made i-th action in round r
		# we can always figure this out from the actions taken, but it's
		# easier to just remember this in multiplayer (because of folds)
		self.action_player = [[0 for r in range(MAX_NUM_ACTIONS)] for i in range(MAX_ROUNDS)]

		# numActions[ r ] gives the number of actions made in round r
		self.num_actions = list(range(MAX_ROUNDS))

		# current round: a value between 0 and game.numRounds-1
		# a showdown is still in numRounds-1, not a separate round
		self.round = None

		# finished is non-zero if and only if the game is over
		self.finished = None

		# playerFolded[ p ] is non-zero if and only player p has folded
		self.player_folded = list(range(MAX_PLAYERS))

		# public cards (including cards which may not yet be visible to players) 
		self.board_cards = list(range(MAX_BOARD_CARDS))

		# private cards
		self.hole_cards = [[0 for c in range(MAX_HOLE_CARDS)] for p in range(MAX_PLAYERS)]


class MatchState():
	def __init__(self):
		self.state = State()
		self.viewing_player = None # integer

def make_card(rank, suit):

	return rank * MAX_SUITS + suit

def rank_of_card(card):

	return card // MAX_SUITS

def suit_of_card(card):

	return card % MAX_SUITS

