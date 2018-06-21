from random import shuffle
from itertools import chain
from Server.predefine import ActionType
from Server.predefine import MAX_RANKS, MAX_SUITS, MAX_NUM_ACTIONS
from sys import maxsize
from Server.logging import log


class Game:

    actionChars = "fcr"
    suitChars = "cdhs"
    rankChars = "23456789TJKA"

    """game is supposed manipulate state instance"""
    def __init__(self, game_def, tryFixing=True):
        self.game_def = game_def
        self.game_type = game_def.game_type
        self.tryFixing = tryFixing

    def init_state(self, state):
        state.game = self
        state.blind = self.game_def.blind[:]
        state.spent = self.game_def.blind[:]
        state.maxSpent = max(state.spent)

        if self.game_type == "nolimit":
            if state.maxSpent:
                state.minNoLimitRaiseTo = 2 * state.maxSpent
            else:
                state.minNoLimitRaiseTo = 1
        elif self.game_type == "limit":
            state.minNoLimitRaiseTo = 0

        state.stack = self.game_def.stack[:] or [maxsize] * self.game_def.numPlayers
        state.playerFolded = [False] * self.game_def.numPlayers
        state.playerAllIned = [False] * self.game_def.numPlayers
        state.numActions = [0] * self.game_def.numRounds
        state.action = [[] for i in range(self.game_def.numRounds)]
        state.actingPlayer = [[] for i in range(self.game_def.numRounds)]
        state.numCalled = 0
        state.numRaises = 0
        state.round = 0
        state.finished = False

    def bcStart(self, rd):
        return sum(self.game_def.numBoardCards[0:rd])

    def sumBoardCards(self, rd):
        return sum(self.game_def.numBoardCards[0:rd+1])

    def nextPlayer(self, state, cp):
        np = cp
        np = (np + 1) % self.game_def.numPlayers
        while state.playerFolded[np] or state.spent[np] >= self.game_def.stack[np]:
            np = (np + 1) % self.game_def.numPlayers
        return np

    def currentPlayer(self, state):
        if state.numActions[state.round]:
            return self.nextPlayer(state, state.actingPlayer[state.round][state.numActions[state.round] - 1])
        return self.nextPlayer(state, self.game_def.firstPlayer[state.round] + self.game_def.numPlayers - 1)

    def numRaises(self, state):
        return state.numRaises

    def numFolded(self, state):
        return state.playerFolded.count(True)

    def numCalled(self, state):
        return state.numCalled

    def numAllIned(self, state):
        return state.playerAllIned.count(True)

    def numActingPlayer(self, state):
        return self.game_def.numPlayers - self.numAllIned(state) - self.numFolded(state)

    def dealCards(self, state):
        deck = self.create_deck()
        shuffle(deck)
        numPlayers, numHoleCards = self.game_def.numPlayers, self.game_def.numHoleCards
        numAllBoardCards = sum(self.game_def.numBoardCards)
        state.holeCards = [deck[i:i+numHoleCards] for i in range(0, numHoleCards*numPlayers, numHoleCards)]
        state.boardCards = deck[numHoleCards*numPlayers:numHoleCards*numPlayers+numAllBoardCards]

    def create_deck(self):
        card_count = self.game_def.numSuits * self.game_def.numRanks
        deck = [None] * card_count
        index = 0
        for s in range(MAX_SUITS - self.game_def.numSuits):
            for r in range(MAX_RANKS - self.game_def.numRanks):
                deck[index] = self.makeCard(rank=r, suit=s)
                index += 1
        return deck

    def raiseIsValid(self, state):
        if self.numRaises(state) >= self.game_def.maxRaises[state.round]:
            return False, None, None
        if state.numActions[state.round] + self.game_def.numPlayers > MAX_NUM_ACTIONS:
            message = "actions is reaching MAX_NUM_ACTIONS, forcing call\n"
            log.warning(msg=message)
            return False, None, None
        if self.numActingPlayers(state) <= 1:
            return False, None, None

        if self.game_type == "limit":
            return True, 0, 0
        elif self.game_type == "nolimit":
            p = self.currentPlayer(state)
            min_ = state.minNoLimitRaiseTo
            max_ = state.stack[p]
            if min_ > state.stack[p]:
                if state.maxSpent >= state.stack[p]:
                    return False, min_, max_
                else:
                    min_ = max_
                    return True, min_, max_

    def isValidAction(self, state, action):
        if self.stateFinished(state) or action.type == ActionType.a_invalid:
            return False
        p = self.currentPlayer(state)
        if action.type == ActionType.a_raise:
            valid, min_, max_ = self.raiseIsValid(state)
            if not valid:
                return False
            if self.game_type == "nolimit":
                if action.size < min_:
                    if not self.tryFixing:
                        return False
                    message = "WARNING: raise of %d increased to %d\n" % (action.size, min_)
                    log.debug(msg=message)
                    action.size = min_
                elif action.size > max_:
                    if not self.tryFixing:
                        return False
                    message = "WARNING: raise of %d decreased to %d\n" % (action.size, max_)
                    log.debug(msg=message)
                    action.size = max_
        elif action.type == ActionType.a_fold:
            if state.spent[p] == state.maxSpent or state.spent[p] == state.stack[p]:
                return False
            if action.size != 0:
                message = "WARNING: size given for fold\n"
                log.debug(msg=message)
                action.size = 0
        else:
            if action.size != 0:
                message = "WARNING: size given for something other than a no-limit raise\n"
                log.debug(msg=message)
                action.size = 0

        return True

    def doAction(self, state, action):
        p = self.currentPlayer(state)
        assert state.numActions[state.round] < MAX_NUM_ACTIONS

        state.action[state.round].append(action)
        state.actingPlayer[state.round].append(p)
        state.numActions[state.round] += 1

        assert len(state.action[state.round]) == state.numActions[state.round]

        if action.type == ActionType.a_fold:
            state.playerFolded[p] = True
        elif action.type == ActionType.a_call:
            if state.maxSpent > state.stack[p]:
                state.spent[p] = state.stack[p]
                state.playerAllIned[p] = True
            else:
                state.spent[p] = state.maxSpent
                state.numCalled += 1
        elif action.type == ActionType.a_raise:
            if self.game_type == "nolimit":
                assert state.maxSpent < action.size <= state.stack[p]

                if action.size * 2 - state.maxSpent > state.minNoLimitRaiseTo:
                    state.minNoLimitRaiseTo = action.size * 2 - state.maxSpent
                state.numCalled = 1
            elif self.game_type == "limit":
                if state.maxSpent + self.game_def.raiseSize[state.round] > state.stack[p]:
                    state.maxSpent = state.stack[p]
                    state.playerAllIned[p] = True
                else:
                    state.maxSpent += state.raiseSize[state.round]
                    state.numCalled = 1
                state.spent[p] = state.maxSpent
        else:
            message = "ERROR: trying to do invalid action %r" % action.type
            log.error(msg=message)
            assert False

        # see if round or game has ended
        if self.numFolded(state) + 1 >= self.game_def.numPlayers:
            state.finished = True
        elif self.numCalled(state) >= self.numActingPlayer(state):
            if self.numActingPlayer(state) > 1:
                if state.round + 1 < self.game_def.numRounds:
                    state.round += 1
                    state.numCalled = 0
                    state.minNoLimitRaiseTo = max(self.game_def.blind)
                    state.minNoLimitRaiseTo += state.maxSpent
                else:
                    # no more betting rounds
                    state.finished = True
            else:
                # no more enough players for betting, but still need a showdown
                state.finished = True
                state.round = self.game_def.numRounds - 1

    def try_do_action(self, state, action):
        if self.isValidAction(state, action):
            self.doAction(state, action)
            return True
        return False

    def stateFinished(self, state):
        return state.finished

    @staticmethod
    def makeCard(self, rank, suit):
        return rank * MAX_SUITS + suit

    @staticmethod
    def rankOfCard(self, card):
        return card // MAX_SUITS

    @staticmethod
    def suitOfCard(self, card):
        return card % MAX_SUITS
