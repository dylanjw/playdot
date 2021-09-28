from functools import wraps
from .constants import (
    WINNING_ROW_LEN,
    DIRECTIONS,
    PlaydotPiece,
)


def count_cardinal(board, x, y, direction, player):
    count = 0
    x_offset, y_offset = DIRECTIONS[direction]

    def inbound(p):
        return board.width > p > -1

    while True:
        x = x + x_offset
        y = y + y_offset
        if not inbound(x) or not inbound(y):
            break
        if not PlaydotPiece(board.get_piece(x, y)) == player:
            break
        count += 1
        if count >= WINNING_ROW_LEN:
            break
    return count


def get_line_count_fn(directions):
    def fn(board, x, y, player):
        piece = PlaydotPiece(board.get_piece(x, y))
        if not piece == player:
            return 0
        count = 1 + sum(
            count_cardinal(board, x, y, d, player) for d in directions
        )
        return count

    return fn


count_row = get_line_count_fn(("E", "W"))
count_col = get_line_count_fn(("N", "S"))
count_fdiag = get_line_count_fn(("NE", "SW"))
count_bdiag = get_line_count_fn(("NW", "SE"))


class MetaAccessor:
    """For use with row meta data

    When a row has no meta data associated with it, it is
    initialized.
    """

    def __init__(self, game):
        self.game = game

    def __getitem__(self, key):
        key = str(key)
        if self.game.data.meta is None:
            self.game.data.meta = {}
        if key not in self.game.data.meta.keys():  # TODO: limit key creation
            print("initializing row metadata")
            print(f"{key} not in {self.game.data.meta.keys()}")
            self.game.data.meta[key] = self._init_row_metadata()
            self.game.data.save()
        return self.game.data.meta[key]

    def __setitem__(self, key, value):
        key = str(key)
        if key not in self.game.data.meta:
            self.game.data.meta[key] = self._init_row_metadata()
        self.game.data.meta[key] = value
        self.game.data.save()

    def _init_row_metadata(self):
        return {
            "peaks": {
                side: conf.bottom for side, conf in self.game.stack_conf.items()
            },
            "is_full": False,
        }


def refresh_data(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        args[0].data.refresh_from_db()
        return fn(*args, **kwargs)

    return wrapper


def get_reverse_bottom(width, inc, bottom):
    # get the converse of bottom for board
    return (width - 1) - bottom
