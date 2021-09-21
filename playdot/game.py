from itertools import cycle
from functools import partial
from copy import copy
from .utils import (
    check_if_in_win,
)
from .constants import (
    EMPTY_DOT,
    WIN_COUNT,
)

class RowFull(Exception):
    pass


def init_board(width):
    row = [EMPTY_DOT]*width
    return [copy(row) for _ in range(width)]


class Board:
    def __init__(self, width=7, board=None):
        if board is None:
            self.board = init_board(width)
        self.row_metadata = {}
        self.width = width

    def __len__(self):
        return self.width

    def __str__(self):
        s = []
        for row in self.board:
            s.append("".join(row))
        return "\n".join(s)

    def __getitem__(self, key):
        return self.board[key]

    def _init_row_metadata(self, y):
        self.row_metadata[y] = {
            "is_full": False,
            "left_peak": None,
            "right_peak": None,
        }

    def get_row_metadata(self, y, key):
        return self.row_metadata[y][key]

    def set_row_metadata(self, y, key, value):
        self.row_metadata[y][key] = value

    def get_peak(self, y, side):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        return self.row_metadata[y][key]

    def set_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        self.row_metadata[y][key] = value

    def move_peak(self, y, side, value):
        if side not in ("L", "R"):
            raise ValueError()
        key = "right_peak" if side == "R" else "left_peak"
        self.row_metadata[y][key] += value

    def set_piece(self, x, y, piece):
        self.board[y][x] = piece

    def get_piece(self, x, y):
        return self.board[y][x]

    def is_piece(self, x, y, piece):
        return self.board[y][x] == piece

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
            return

        # shift pieces
        # iterate from top of peak to bottom
        # e.g. for right -> (3,4,...,width-1)
        #      for left  -> (5,4,...,0)
        for x in range(self.get_peak(y, side), bottom-stack_inc, -(stack_inc)):
            print(f"x, y = ({x},{y})")
            piece = self.get_piece(x, y)
            self.set_piece(x + stack_inc, y, piece)
        # set new piece
        self.set_piece(bottom, y, player)
        self.move_peak(y, side, stack_inc)
        print(f"peak moved to {self.get_peak(y, side)}")
        above_peak_index = self.get_peak(y, side) + stack_inc
        if not self.is_piece(above_peak_index, y, EMPTY_DOT):
            self.set_row_metadata(y, "is_full", True)
        return

    def do_move(self, player, side, y):
        if not y in self.row_metadata.keys():
            self._init_row_metadata(y)
        if self.row_metadata[y]["is_full"]:
            raise RowFull("Can't place piece, row full")

        return self._do_move(player, side, y)


def do_player_turn(board, player, side, y):
    board.do_move(player, side, y)
    print(board)
    if side == "R":
        peak = board.row_metadata[y]["right_peak"]
        for x in range(peak, board.width):
            if check_if_in_win(board, (x, y)):
                return f"{board.board[y][x]} wins!"
    if side == "L":
        peak = board.row_metadata[y]["left_peak"]
        for x in range(peak, -1, -1):
            if check_if_in_win(board, (x, y)):
                return f"{board.board[y][x]} wins!"


def run_game():
    print("Game move format {R|L}D, e.g. R5")
    board = Board(7)
    players = cycle("XO")
    for player in players:
        while True:
            move = input(f"Player {player}'s turn: ")
            if len(move) != 2:
                print("Error, invalid move")
                continue
            side, y = move
            y = int(y)
            if not side in ("L", "R"):
                print("Error, invalid move")
                continue
            try:
                wins = do_player_turn(board, player, side, y)
            except RowFull:
                print("Error, invalid move. Row full")
                continue
            break
        if wins is not None:
            print(wins)
            break
