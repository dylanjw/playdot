from playdot.utils import (
    count_cardinal,
    count_row,
    count_col,
    count_bdiag,
    count_fdiag,
    check_if_in_win,
)


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

def test_count_cardinal_from_edge():
    count = count_cardinal(
        TEST_BOARD,
        (6, 0),
        "NE",
        "X")
    assert count == 0


def test_count_cardinal_single_edge():
    count = count_cardinal(
        TEST_BOARD,
        (6, 6),
        "NE",
        "O")
    assert count == 0


def test_count_cardinal_four():
    count = count_cardinal(
        TEST_BOARD,
        (0, 6),
        "NE",
        "X")
    assert count == 3


def test_count_cardinal_east():
    count = count_cardinal(
        TEST_BOARD,
        (1, 1),
        "E",
        "X")
    assert count == 0


def test_count_cardinal_west():
    count = count_cardinal(
        TEST_BOARD,
        (1, 1),
        "W",
        "X")
    assert count == 1


def test_count_row():
    assert count_row(TEST_BOARD, (0,1), "X") == 2

def test_count_col():
    assert count_col(TEST_BOARD, (6, 3), "X") == 3

def test_count_fdiag():
    assert count_fdiag(TEST_BOARD, (1, 4), "X") == 3

def test_count_bdiag():
    assert count_bdiag(TEST_BOARD, (1, 4), "X") == 2

def test_check_if_in_win():
    assert check_if_in_win(TEST_BOARD, (1, 2)) is True
    assert check_if_in_win(TEST_BOARD, (2, 2)) is False
