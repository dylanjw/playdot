from .constants import (
    WIN_COUNT,
    DIRECTIONS,
    EMPTY_DOT,
)


def count_cardinal(
        board,
        point: tuple,
        direction,
        player):
    count = 0
    x, y = point
    x_offset, y_offset = DIRECTIONS[direction]
    width = len(board)
    inbound =  lambda p: width > p > -1
    on_player = True
    while True:
        x = x + x_offset
        y = y + y_offset
        if not inbound(x) or not inbound(y):
            break
        if board[y][x] != player:
            break
        count += 1
        if count >= WIN_COUNT:
            break
    return count


def get_line_count_fn(directions):
    def fn(board, point, player):
        x, y = point
        if board[y][x] != player:
            return 0
        count = 1 + sum(
            count_cardinal(board, point, d, player) for d in directions
        )
        return count
    return fn


count_row = get_line_count_fn(("E", "W"))
count_col = get_line_count_fn(("N", "S"))
count_fdiag = get_line_count_fn(("NE", "SW"))
count_bdiag = get_line_count_fn(("NW", "SE"))


def check_if_in_win(board, point):
    x, y = point
    piece = board[y][x]
    if piece == EMPTY_DOT:
        return False
    if any(map(
            lambda c: c >= WIN_COUNT,
            (
                count_row(board, point, piece),
                count_col(board, point, piece),
                count_bdiag(board, point, piece),
                count_fdiag(board, point, piece)))):
        return True
    return False
