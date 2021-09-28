import json
from django.urls import reverse
import pytest

from playdot.views import list_rooms, create, game_state, move
from playdot.game import Game


def test_list_rooms_empty(db, client):
    response = client.get(reverse(list_rooms))
    assert len(json.loads(response.content)["games"]) == 0


@pytest.fixture()
def create_games(db):
    return [Game(board_width=7).gid, Game(board_width=7).gid]


def test_list_rooms_two(client, db, create_games):
    gid1, gid2 = create_games
    response = client.get(reverse(list_rooms))
    assert len(json.loads(response.content)["games"]) == 2


def test_create(client, db):
    response = client.post(reverse(create, kwargs={"width": 7}))
    room_info = json.loads(response.content)
    assert room_info["board_width"] == 7


def test_get_board_state(client, db, create_games):
    gid, _ = create_games
    response = client.get(reverse(game_state, kwargs={"gid": gid}))
    board_state = json.loads(response.content)
    assert len(board_state["board"]) == 0


def test_make_move(client, db, create_games):
    player = 1
    side = "R"
    y = "0"
    gid, _ = create_games
    response = client.post(
        reverse(move, kwargs={"gid": gid}),
        data={"y": y, "side": side, "player": player},
        content_type="application/json",
    )
    assert response.content.decode() == "success"

    response = client.get(reverse(game_state, kwargs={"gid": gid}))
    board_data = json.loads(response.content)
    assert board_data["board"][0] == {"x": 6, "y": 0, "value": 1}
