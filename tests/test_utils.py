import pytest
import uuid
from playdot.utils import (
    count_cardinal,
    count_row,
    count_col,
    count_bdiag,
    count_fdiag,
    get_reverse_bottom,
)
from playdot.models import GameData, GridBoard
from playdot.constants import PlaydotPiece


TEST_BOARD_STR = """
_______
XX_____
XXX___X
XXXX__X
XXXO__X
XXO__XO
XXO__XO
"""


def test_get_reverse_bottom():
    assert get_reverse_bottom(7, 1, -1) == 7
    assert get_reverse_bottom(7, -1, 7) == -1


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
            convert = {"X": 1, "O": 2, "_": 0}
            piece = convert[piece]
            game_board.set_piece(x, y, piece)
    return game_board


@pytest.mark.parametrize(
    "x,y,direction,player,expected_count",
    (
        (6, 0, "NE", PlaydotPiece(1), 0),
        (6, 6, "NE", PlaydotPiece(2), 0),
        (0, 6, "NE", PlaydotPiece(1), 3),
        (1, 1, "E", PlaydotPiece(1), 0),
        (1, 1, "W", PlaydotPiece(1), 1),
    ),
)
@pytest.mark.django_db()
def test_count_cardinal_from_edge(
    board, x, y, direction, player, expected_count
):
    count = count_cardinal(board, x, y, direction, player)
    assert count == expected_count


def test_count_row(board):
    assert count_row(board, 0, 1, PlaydotPiece(1)) == 2


def test_count_col(board):
    assert count_col(board, 6, 3, PlaydotPiece(1)) == 3


def test_count_fdiag(board):
    assert count_fdiag(board, 1, 4, PlaydotPiece(1)) == 3


def test_count_bdiag(board):
    assert count_bdiag(board, 1, 4, PlaydotPiece(1)) == 2
