from abc import (
    ABC,
    abstractmethod,
)
from copy import copy
from uuid import uuid4
from .constants import (
    EMPTY_DOT,
)
from . import models


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
    def get_metadata(self, bid, **kwargs):
        pass

    @abstractmethod
    def set_metadata(self, bid, **kwargs):
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


class DjangoModelBackend(BaseBoardBackend):
    def new_board(self, width):
        bid = self.generate_id()
        b = models.Board(bid=bid, width=width)
        b.save()
        return bid

    def get_metadata(self, bid, **kwargs):
        board = models.Board.objects.get(bid=bid)
        if not 'y' in kwargs:
            return getattr(board, kwargs['key'])
        try:
            row = models.Row.objects.get(board=board, y=kwargs["y"])
        except models.Row.DoesNotExist:
            raise EmptyRow()
        return getattr(row, kwargs["key"])

    def set_metadata(self, bid, **kwargs):
        board = models.Board.objects.get(bid=bid)
        if not 'y' in kwargs:
            setattr(board, kwargs['key'], kwargs['value'])
            board.save()
            return
        try:
            row = models.Row.objects.get(board=board, y=kwargs["y"])
        except models.Row.DoesNotExist:
            row = models.Row(board=board, y=kwargs["y"])
        setattr(row, kwargs["key"], kwargs["value"])
        row.save()

    def set_piece(self, bid, x, y, piece):
        print(f"!!!!piece value is: {piece}")
        board = models.Board.objects.get(bid=bid)
        try:
            row = models.Row.objects.get(board=board, y=y)
        except models.Row.DoesNotExist:
            row = models.Row(bid=bid, y=y)
            row.save()
        try:
            space = models.Space.objects.get(board=board, row=row, x=x)
            space.value = piece
        except models.Space.DoesNotExist:
            space = models.Space(board=board, row=row, value=piece, x=x)
        space.save()

    def get_piece(self, bid, x, y):
        try:
            board = models.Board.objects.get(bid=bid)
            row = models.Row.objects.get(board=board, y=y)
            space = models.Space.objects.get(board=board, row=row, x=x)
        except models.Space.DoesNotExist:
            return EMPTY_DOT
        return space.value

    def is_piece(self, bid, x, y, piece):
        board = models.Board.objects.get(bid=bid)
        try:
            row = models.Row.objects.get(board=board, y=y)
        except models.Row.DoesNotExist:
            if piece == EMPTY_DOT:
                return True
            return False
        exists = models.Space.objects.filter(board=board, row=row, x=x, value=piece).exists()
        if not exists and piece == EMPTY_DOT:
            return True
        return exists

    def to_string(self, bid):
        board = models.Board.objects.get(bid=bid)
        rows = models.Row.objects.filter(board=board).order_by('-y')
        as_string = ""
        for y in range(board.width):
            try:
                row = rows.get(y=y)
                spaces = models.Space.objects.filter(board=board, row=row).order_by('-x')
                for x in range(board.width):
                    try:
                        space = spaces.get(x=x)
                        as_string = as_string + str(space.value)
                    except models.Space.DoesNotExist:
                        as_string = as_string + "_"
            except models.Row.DoesNotExist:
                as_string = as_string + "_" * board.width
            as_string = as_string + ("\n")
        return as_string


BOARD_DATA = {"boards": {}}

class GlobalVarBackend(BaseBoardBackend):
    def __init__(self):
        self.data = BOARD_DATA

    def new_board(self, width):
        bid = self.generate_id()
        row = [EMPTY_DOT]*width
        self.data['boards'][bid] = {'board': [], 'metadata': {}}
        self.data['boards'][bid]['board'] = [copy(row) for _ in range(width)]
        self.data['boards'][bid]['width'] = width
        return bid

    def get_metadata(self, bid, **kwargs):
        if 'y' in kwargs:
            if kwargs["y"] not in self.data['boards'][bid]["metadata"]:
                raise EmptyRow()
            return self.data['boards'][bid]["metadata"][kwargs["y"]][kwargs["key"]]
        return self.data['boards'][bid][kwargs["key"]]


    def set_metadata(self, bid, **kwargs):
        if 'y' in kwargs:
            if kwargs['y'] not in self.data['boards'][bid]['metadata']:
                self.data['boards'][bid]['metadata'][kwargs['y']] = {}
            self.data['boards'][bid]['metadata'][kwargs['y']][kwargs['key']] = kwargs['value']
        else:
            self.data['boards'][bid][kwargs["key"]] = kwargs["value"]

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
    def __init__(self, width=None, bid=None, backend=GlobalVarBackend):
        self.backend = backend()
        if bid is None and width is None:
            raise TypeError("Can't create a new board without a width")
        if bid is None:
            self.bid = self.backend.new_board(width)
        else:
            self.bid = bid
            self.width = self.backend.get_metadata(self.bid, key='width')
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
        return self.backend.get_metadata(self.bid, y=y, key=key)

    def set_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        self.backend.set_metadata(self.bid, y=y, key=key, value=value)

    def move_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        peak = self.backend.get_metadata(self.bid, y=y, key=key)
        self.backend.set_metadata(self.bid, y=y, key=key, value=peak + value)

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
            self.backend.set_metadata(self.bid, y=y, key="is_full", value=True)
        self.last_altered = [
            (x, y) for x in [self.get_peak(y, side)] + list(stack)
        ]
        return

    def do_move(self, player, side, y):
        try:
            if self.backend.get_metadata(self.bid, y=y, key="is_full"):
                raise RowFull("Can't place piece, row full")
        except EmptyRow:
            for key, value in self.default_row_metadata:
                self.backend.set_metadata(self.bid, y=y, key=key, value=value)

        return self._do_move(player, side, y)
