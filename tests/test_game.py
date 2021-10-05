from playdot.game import generate_random_move


def test_generate_random_move():
    side, y = generate_random_move(7)
    assert side in ("R", "L")
    assert isinstance(y, int)
