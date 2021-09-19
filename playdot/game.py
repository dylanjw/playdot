from copy import copy

WIDTH = 7
EMPTY = "_"

row = [EMPTY]*WIDTH
board = [copy(row) for _ in range(WIDTH)]

TEST_BOARD_STR = """
_______
XX_____
XXX___X
XXXX__X
XXXO__X
XXO__XO
XXO__XO
"""

TEST_BOARD = TEST_BOARD_STR.split()



def to_list(fn):
    def inner(*args, **kwargs):
        return list(fn(*args, **kwargs))
    return inner



def check_row(row):
    ...

@to_list
def get_cols(board):
    width = len(board)
    for x in range(width):
        yield [board[y][x] for y in range(width)]
