import uuid
from . import utils, constants
from .models import (
    PlaydotGameData,
    Space,
)
from dataclasses import dataclass
from enum import Enum


class RowFull(Exception):
    pass


class GameNotFound(Exception):
    pass


class PlaydotPiece(Enum):
    ONE = 1
    TWO = 2
    BLANK = 0


@dataclass
class StackConf:
    inc: int = None
    bottom: int = None


def get_stack_conf(board_width):
    return {
        "R": StackConf(inc=-1, bottom=board_width - 1),
        "L": StackConf(inc=1, bottom=0),
    }


class Game:
    meta = utils.MetaAccessor()

    def __init__(self, gid=None, board_width=None):
        self.init_game_data = PlaydotGameData.new
        if board_width is None and gid is None:
            raise TypeError(
                "Must supply a value for board_width"
                "when initializing a new game"
            )

        if gid is None:
            self.new_game(board_width)
        else:
            self.load_game(gid)

        self.gid = self.data.gid
        self.board_width = self.data.board.width
        self.stack_conf = get_stack_conf(self.board_width)

    def load_game(self, gid):
        if PlaydotGameData.objects.filter(gid=gid).exists():
            self.data = PlaydotGameData.objects.get(gid=gid)
        else:
            raise GameNotFound()

    def new_game(self, board_width):
        gid = uuid.uuid4()
        self.data = self.init_game_data(gid, board_width)

    @utils.refresh_data
    def _get_peak(self, y, side):
        return self.meta[y]["peaks"][side]

    @utils.refresh_data
    def _bump_peak(self, y, side):
        inc = self.stack_conf[side].inc
        self.meta[y]["peaks"][side] += inc

    def _check_if_row_full(self, y, side):
        x_above_peak = self._get_peak(y, side) + self.stack_conf[side].inc
        if self.data.board.get_piece(x_above_peak, y) != PlaydotPiece.BLANK:
            return True
        return False

    def _check_if_in_win(self, x, y):
        piece = self.data.board.get_piece(x, y)
        if piece == PlaydotPiece.BLANK:
            return False
        if any(
            map(
                lambda c: c >= constants.WINNING_ROW_LEN,
                (
                    utils.count_row(self.data.board, x, y, piece),
                    utils.count_col(self.data.board, x, y, piece),
                    utils.count_bdiag(self.data.board, x, y, piece),
                    utils.count_fdiag(self.data.board, x, y, piece),
                ),
            )
        ):
            return True
        return False

    def do_move(self, side, y, piece):
        y = int(y)
        if self.meta[y]["is_full"]:
            raise RowFull()
        s = self.stack_conf[side]
        peak = self._get_peak(y, side)
        stack_x_coord = range(peak, s.bottom - s.inc, -(s.inc))
        for x in stack_x_coord:
            shifting_piece = self.data.board.get_piece(y, x)
            if shifting_piece == 0:
                continue
            self.data.board.set_piece(x + s.inc, y, shifting_piece)
            self._check_if_in_win(x + s.inc, y)
        self.data.board.set_piece(s.bottom, y, piece)
        self._check_if_in_win(s.bottom, y)
        self._bump_peak(y, side)
        if self._check_if_row_full(y, side):
            self.meta[y]["is_full"] = True
        self.data.save()

    def as_dict(self):
        return {
            "gid": self.gid,
            "board_width": self.board_width,
            "board": self.board_as_dict(),
        }

    def board_as_dict(self):
        filled_spaces = Space.objects.filter(board=self.data.board)
        return [
            {"x": space.x, "y": space.row.y, "value": space.value}
            for space in filled_spaces
        ]
