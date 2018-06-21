class State():
    def __init__(self):
        self.game = None
        self.handId = None
        self.maxSpent = None  # largest bet so far, including all previous rounds
        self.spent = None
        self.action = None
        self.actionPlayer = None
        self.numActions = None
        self.round = None
        self.finished = None
        self.boardCards = None
        self.holeCards = None
        self.playerFolded = None
        self.playerAllIned = None
        self.numCalled = None
        self.numRaises = None

        self.minNoLimitRaiseTo = None  # only used for noLimitBetting games

    def __str__(self):
        pass

    def display(self):
        attrs = ["stack", "spent", "playerFolded", "playerAllIned", "holeCards", "boardCards", "numCalled",
                 "round", "finished", "round"]
        d = {}
        for attr in attrs:
            d[attr] = getattr(self, attr, None)
        print(d)


class MatchState:
    def __init__(self, state=None, viewingPlayer=None):
        self.state = state
        self.viewingPlayer = viewingPlayer
