import re
from Server.game_definition import GameDefinition
from Server.game import Game


class GameFactory:

    def __init__(self):
        self.game_def = GameDefinition()
        self.numbers_regex = re.compile(r"[\d]+")

    def read_game(self, file):
        with open(file, "r") as f:
            lines = [line.strip("\n").strip("\r") for line in f.readlines()]

        assert lines[0] == self.game_def.prefix
        assert lines[-1] == self.game_def.suffix
        assert lines[1] in ("limit", "nolimit")
        self.game_def.game_type = lines[1]

        for line in lines[2:]:
            if line.startswith("#"):
                continue
            for attr in self.game_def.attrs:
                value = self.parse(line, attr)
                if value:
                    setattr(self.game_def, attr, getattr(self.game_def, attr, None) or value)

        self.game_def.firstPlayer = [x-1 for x in self.game_def.firstPlayer]

    def parse(self, string, prefix):
        if string.startswith(prefix):
            numbers = self.numbers_regex.findall(string)
            numbers = [int(number) for number in numbers]
            return numbers[0] if len(numbers) == 1 else numbers
        return None

    def print_game(self):
        print(self.game_def)

    def get_game(self):
        """read_game must be called before"""
        return Game(self.game_def)

