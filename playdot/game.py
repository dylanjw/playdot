from itertools import cycle
from .utils import (
    check_if_in_win,
)
from .board import (
    Board,
    RowFull,
)


def do_player_turn(board, player, side, y):
    board.do_move(player, side, y)
    for x, y in board.last_altered:
        check_if_in_win(board, (x, y))


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
            if side not in ("L", "R"):
                print("Error, invalid move")
                continue
            try:
                wins = do_player_turn(board, player, side, y)
            except RowFull:
                print("Error, invalid move. Row full")
                continue
            break
        print(board)
        if wins is not None:
            print(wins)
            break
