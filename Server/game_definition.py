class GameDefinition:

    def __init__(self):
        self.prefix = "GAMEDEF"
        self.suffix = "END GAMEDEF"
        self.game_type = None

        self.bettingType = None
        self.limit = None
        self.numPlayers = None
        self.numRounds = None
        self.stack = None
        self.blind = None
        self.raiseSize = None
        self.firstPlayer = None
        self.maxRaises = None
        self.numSuits = None
        self.numRanks = None
        self.numHoleCards = None
        self.numBoardCards = None

        self.attrs = ["numPlayers", "numRounds", "stack", "blind", "raiseSize", "firstPlayer", "maxRaises",
                      "numSuits", "numRanks", "numHoleCards", "numBoardCards"]

    def __str__(self):
        strings = []
        strings.append(self.prefix)
        strings.append(self.game_type)

        for attr in self.attrs:
            value = getattr(self, attr, None)
            if value:
                strings.append("%s = %s" % (attr, self.attr_value_to_string(value)))

        strings.append(self.suffix)

        return "\n".join(strings)


    @staticmethod
    def attr_value_to_string(value):
        if isinstance(value, (int,)):
            return str(value)
        elif isinstance(value, (list,)):
            return " ".join([str(x) for x in value])
        raise Exception

