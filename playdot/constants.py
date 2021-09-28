from enum import Enum


class PlaydotPiece(Enum):
    ONE = 1
    TWO = 2
    BLANK = 0


DIRECTIONS = {
    "W": (-1, 0),
    "E": (1, 0),
    "S": (0, 1),
    "N": (0, -1),
    "SE": (1, 1),
    "SW": (-1, 1),
    "NW": (-1, -1),
    "NE": (1, -1),
}

WINNING_ROW_LEN = 4
