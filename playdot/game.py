import uuid
from . import utils, constants
from .models import (
    PlaydotPiece,
    PlaydotGameData,
    Space,
)
from dataclasses import dataclass
import random


class RowFull(Exception):
    pass


class GameNotFound(Exception):
    pass


class GameOver(Exception):
    pass


@dataclass
class StackConf:
    inc: int = None
    bottom: int = None


def get_other_player(piece: PlaydotPiece):
    if piece == PlaydotPiece.ONE:
        return PlaydotPiece.TWO
    else:
        return PlaydotPiece.ONE


def get_stack_conf(board_width):
    return {
        "R": StackConf(inc=-1, bottom=board_width),
        "L": StackConf(inc=1, bottom=-1),
    }


class Game:
    def __init__(self, gid=None, board_width=None, is_single_player=False):
        self.init_game_data = PlaydotGameData.new
        if board_width is None and gid is None:
            raise TypeError(
                "Must supply a value for board_width"
                "when initializing a new game"
            )

        if gid is None:
            self.data = self.new_game(board_width, is_single_player)
        else:
            self.data = self.load_game(gid)

        self.gid = self.data.gid
        self.board_width = self.data.board.width
        self.stack_conf = get_stack_conf(self.board_width)
        self.meta = utils.MetaAccessor(self)

        if self.data.is_single_player:
            self.do_move = self._do_single_player_move
        else:
            self.do_move = self._do_regular_move

    def load_game(self, gid):
        if PlaydotGameData.objects.filter(gid=gid).exists():
            return PlaydotGameData.objects.get(gid=gid)
        else:
            raise GameNotFound()

    def new_game(self, board_width, is_single_player):
        gid = uuid.uuid4()
        return self.init_game_data(gid, board_width, is_single_player)

    @utils.refresh_data
    def _get_peak(self, y, side):
        return self.meta[y]["peaks"][side]

    @utils.refresh_data
    def _bump_peak(self, y, side):
        inc = self.stack_conf[side].inc
        self.meta[y]["peaks"][side] += inc
        self.data.save()

    def _check_if_row_full(self, y, side):
        print("checking if row is full")
        s = self.stack_conf[side]
        x_above_peak = self._get_peak(y, side) + s.inc
        max_x = utils.get_reverse_bottom(self.board_width, s.inc, s.bottom)
        print(f"x_above_peak: {x_above_peak}, max_x:{max_x}")
        if x_above_peak == max_x:
            return True
        piece_value = self.data.board.get_piece(x_above_peak, y)
        print(f"piece_value: {piece_value}")
        if PlaydotPiece(piece_value) != PlaydotPiece.BLANK:
            print("not blank")
            return True
        return False

    def _check_if_in_win(self, x, y):
        piece = PlaydotPiece(self.data.board.get_piece(x, y))
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
            print(f"{piece} won the game")
            self.data.winner = piece.value
            self.data.save()

    @utils.refresh_data
    def _do_regular_move(self, side, y, piece_value: int):
        piece = PlaydotPiece(piece_value)
        if piece.value != self.data.next_to_play:
            print("blocking move")
            return
        y = int(y)
        if self.meta[y]["is_full"]:
            raise RowFull()
        if self.data.winner:
            raise GameOver()
        s = self.stack_conf[side]
        peak = self._get_peak(y, side)
        stack_x_coord = range(peak + s.inc, s.bottom, -(s.inc))
        for x in stack_x_coord:
            shifting_piece = PlaydotPiece(self.data.board.get_piece(x, y))
            if shifting_piece == PlaydotPiece.BLANK:
                continue
            print("Shifting!")
            self.data.board.set_piece(x + s.inc, y, shifting_piece.value)
            self._check_if_in_win(x + s.inc, y)
        self.data.board.set_piece(s.bottom + s.inc, y, piece.value)
        self._check_if_in_win(s.bottom + s.inc, y)
        self._bump_peak(y, side)
        if self._check_if_row_full(y, side):
            print("Row is full!")
            self.meta[y]["is_full"] = True
        self.data.next_to_play = get_other_player(piece).value
        self.data.board.save()
        self.data.save()

    def as_dict(self):
        winner = None
        if self.data.winner:
            winner = self.data.winner
        return {
            "gid": self.gid,
            "board_width": self.board_width,
            "board": self.board_as_dict(),
            "next_player": self.data.next_to_play,
            "winner": winner,
        }

    def board_as_dict(self):
        filled_spaces = Space.objects.filter(board=self.data.board)
        return [
            {"x": space.x, "y": space.row.y, "value": space.value}
            for space in filled_spaces
        ]

    def _do_single_player_move(self, side, y, piece_value):
        self._do_regular_move(side, y, piece_value)
        bot_piece = get_other_player(PlaydotPiece(piece_value))
        while True:
            side, y = generate_random_move(self.board_width)
            if self.check_if_valid_move(side, y):
                break
        self._do_regular_move(side, y, bot_piece)

    def check_if_valid_move(self, side, y):
        return not self._check_if_row_full(y, side)


def generate_random_move(board_width):
    side = random.choice(("R", "L"))
    y = random.choice(range(board_width))
    return side, y
