
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
    a_invalid = NUM_ACTION_TYPES  # =3


@unique
class BettingType(Enum):
    limitBetting = 0
    noLimitBetting = 1


class Action:
    def __init__(self, type=ActionType.a_invalid, size=0):
        self.type = type
        self.size = size
