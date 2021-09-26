import pytest
import uuid
from playdot.utils import (
    count_cardinal,
    count_row,
    count_col,
    count_bdiag,
    count_fdiag,
)
from playdot.game import Game
from playdot.models import GameData, GridBoard


TEST_BOARD_STR = """
_______
XX_____
XXX___X
XXXX__X
XXXO__X
XXO__XO
XXO__XO
"""


@pytest.fixture()
def board(db):
    gid = uuid.uuid4()
    test_board_rows = TEST_BOARD_STR.split()
    width = len(test_board_rows)
    game_board = GridBoard(width=width)
    game_board.save()
    gd = GameData(gid=gid, board=game_board)
    gd.save()
    for y in range(width):
        for x in range(width):
            piece = test_board_rows[y][x]
            game_board.set_piece(x, y, piece)
    return game_board

@pytest.mark.parametrize(
    "x,y,direction,player,expected_count",
    (
        (6, 0, "NE", "X", 0),
        (6, 6, "NE", "0", 0),
        (0, 6, "NE", "X", 3),
        (1, 1, "E", "X", 0),
        (1, 1, "W", "X", 1),
    )
)
@pytest.mark.django_db()
def test_count_cardinal_from_edge(board, x, y, direction, player, expected_count):
    count = count_cardinal(
        board,
        x, y,
        direction,
        player)
    assert count == expected_count



def test_count_row(board):
    assert count_row(board, 0, 1, "X") == 2

def test_count_col(board):
    assert count_col(board, 6, 3, "X") == 3

def test_count_fdiag(board):
    assert count_fdiag(board, 1, 4, "X") == 3

def test_count_bdiag(board):
    assert count_bdiag(board, 1, 4, "X") == 2
