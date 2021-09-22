from abc import (
    ABC,
    abstractmethod,
)
from copy import copy
from uuid import uuid4
from .constants import (
    EMPTY_DOT,
)


class RowFull(Exception):
    pass


class EmptyRow(Exception):
    pass


class BaseBoardBackend(ABC):
    def generate_id(self):
        return uuid4()

    @abstractmethod
    def new_board(self, width):
        pass

    @abstractmethod
    def get_metadata(self, bid, y, key):
        pass

    @abstractmethod
    def set_metadata(self, bid, y, key, value):
        pass

    @abstractmethod
    def set_piece(self, bid, x, y, piece):
        pass

    @abstractmethod
    def get_piece(self, bid, x, y):
        pass

    @abstractmethod
    def is_piece(self, bid, x, y, piece):
        pass

    @abstractmethod
    def to_string(self, bid):
        pass


class MemoryBackend(BaseBoardBackend):
    def __init__(self):
        self.data = {"boards": {}}

    def new_board(self, width):
        bid = self.generate_id()
        row = [EMPTY_DOT]*width
        self.data['boards'][bid] = {'board': [], 'metadata': {}}
        self.data['boards'][bid]['board'] = [copy(row) for _ in range(width)]
        return bid

    def get_metadata(self, bid, y, key):
        if y not in self.data['boards'][bid]["metadata"]:
            raise EmptyRow()
        return self.data['boards'][bid]["metadata"][y][key]

    def set_metadata(self, bid, y, key, value):
        if y not in self.data['boards'][bid]['metadata']:
            self.data['boards'][bid]['metadata'][y] = {}
        self.data['boards'][bid]['metadata'][y][key] = value

    def get_piece(self, bid, x, y):
        return self.data['boards'][bid]['board'][y][x]

    def set_piece(self, bid, x, y, piece):
        self.data['boards'][bid]['board'][y][x] = piece

    def is_piece(self, bid, x, y, piece):
        return self.data['boards'][bid]['board'][y][x] == piece

    def to_string(self, bid):
        s = []
        for row in self.data['boards'][bid]["board"]:
            s.append("".join(row))
        return "\n".join(s)


class Board:
    def __init__(self, width=7, bid=None, backend=MemoryBackend):
        self.backend = backend()
        if bid is None:
            self.bid = self.backend.new_board(width)
        self.width = width
        self.last_altered = None
        self.default_row_metadata = (
            ("is_full", False),
            ("left_peak", None),
            ("right_peak", None)
        )

    def __len__(self):
        return self.width

    def __str__(self):
        return self.backend.to_string(self.bid)

    def get_peak(self, y, side):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        return self.backend.get_metadata(self.bid, y, key)

    def set_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        self.backend.set_metadata(self.bid, y, key, value)

    def move_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        peak = self.backend.get_metadata(self.bid, y, key)
        self.backend.set_metadata(self.bid, y, key, peak + value)

    def set_piece(self, x, y, piece):
        return self.backend.set_piece(self.bid, x, y, piece)

    def get_piece(self, x, y):
        return self.backend.get_piece(self.bid, x, y)

    def is_piece(self, x, y, piece):
        return self.backend.is_piece(self.bid, x, y, piece)

    def _do_move(self, player, side, y):
        if side == "R":
            stack_inc = -1
            bottom = self.width - 1
        if side == "L":
            stack_inc = 1
            bottom = 0

        # initial move on row
        if self.get_peak(y, side) is None:
            self.set_peak(y, side, bottom)
            self.set_piece(bottom, y, player)
            self.last_altered = [(bottom, y)]
            return

        # shift pieces
        # iterate from top of peak to bottom
        # e.g. for right -> (3,4,...,width-1)
        #      for left  -> (5,4,...,0)
        stack = range(self.get_peak(y, side), bottom-stack_inc, -(stack_inc))
        for x in stack:
            print(f"x, y = ({x},{y})")
            piece = self.get_piece(x, y)
            self.set_piece(x + stack_inc, y, piece)
        # set new piece
        self.set_piece(bottom, y, player)
        self.move_peak(y, side, stack_inc)
        print(f"peak moved to {self.get_peak(y, side)}")
        above_peak_index = self.get_peak(y, side) + stack_inc
        if not self.is_piece(above_peak_index, y, EMPTY_DOT):
            self.backend.set_metadata(self.bid, y, "is_full", True)
        self.last_altered = [
            (x, y) for x in [self.get_peak(y, side)] + list(stack)
        ]
        return

    def do_move(self, player, side, y):
        try:
            if self.backend.get_metadata(self.bid, y, "is_full"):
                raise RowFull("Can't place piece, row full")
        except EmptyRow:
            for key, value in self.default_row_metadata:
                self.backend.set_metadata(self.bid, y, key, value)

        return self._do_move(player, side, y)
