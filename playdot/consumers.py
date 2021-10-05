#!/usr/bin/env python3
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .game import Game, PlaydotPiece, RowFull, GameOver
from .models import ChannelPlayer
from django.db import IntegrityError
import random


def try_assign_player_to_channel(game_data, piece, channel_name) -> bool:
    """Attempt to assign a player to a channel

    Returns True when this piece is (or already is) assigned to channel.

    """
    try:
        # We try to create a player assignment and see if it succeeds,
        # avoiding a race condition between checking and assigning.
        ChannelPlayer(
            game=game_data, playing_as=piece.value, channel_name=channel_name
        ).save()
        return True
    # Django throws an IntegrityError when a unique contraint is violated.
    except IntegrityError:
        if ChannelPlayer.objects.filter(
            game=game_data, playing_as=piece.value, channel_name=channel_name
        ).exists():
            return True
        return False


async def get_player_assignment(game_data, channel_name):
    for piece in (PlaydotPiece.ONE, PlaydotPiece.TWO):
        created = await database_sync_to_async(try_assign_player_to_channel)(
            game_data, piece, channel_name
        )

        if created:
            player = piece.value
            break
    else:
        player = "observer"
    return player


class PlaydotBot(AsyncJsonWebsocketConsumer):
    games = {}

    async def join_game(self, content):
        gid = content["data"]["gid"]
        group_name = "playdot_%s" % gid
        game = await database_sync_to_async(Game)(gid=gid)

        await self.channel_layer.group_add(group_name, self.channel_name)

        player = await get_player_assignment(game.data, self.channel_name)
        self.games[gid] = player
        await self.update({'gid': gid})

    async def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(self.group_name, self.channel_name)
        assignments = await database_sync_to_async(
            ChannelPlayer.objects.filter
        )(channel_name=self.channel_name)

        print(f"Bot found assignments that im removing")
        await database_sync_to_async(assignments.delete)()

    async def update(self, event):
        """We handle the `update` event type

        This event is sent when there has been a change to the board state
        """
        print(f"worker received event: {event}")
        player = self.games[event["gid"]]
        game = await database_sync_to_async(Game)(gid=event["gid"])
        if player == game.data.next_to_play:
            side = random.choice(("L", "R"))
            y = random.choice(range(game.board_width))
            await database_sync_to_async(do_turn)(game, side, y, player)

            group_name = "playdot_%s" % event["gid"]
            await self.channel_layer.group_send(
                group_name,
                {"type": "update",
                    "gid": event["gid"] },
            )



class GameConsumer(AsyncJsonWebsocketConsumer):
    game = None

    async def connect(self):
        self.game_id = str(self.scope["url_route"]["kwargs"]["gid"])
        self.game = await database_sync_to_async(Game)(gid=self.game_id)
        self.group_name = "playdot_%s" % self.game_id

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Player assignment
        player = await get_player_assignment(self.game.data, self.channel_name)
        await self.send_json({"method": "assign_player", "data": player})
        self.player = player

    async def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(self.group_name, self.channel_name)
        assignments = await database_sync_to_async(
            ChannelPlayer.objects.filter
        )(channel_name=self.channel_name)
        print(f"found assignments that im removing")
        await database_sync_to_async(assignments.delete)()

    async def receive_json(self, content):
        print(f"received message {content}")
        if content["method"] == "move":
            try:
                await database_sync_to_async(do_turn)(
                    self.game, **content["data"]
                )
            except RowFull:
                await self.send_json(
                    {"method": "invalid_move", "data": "That row is full"}
                )
            except GameOver:
                await self.send_json(
                    {"method": "game_over", "data": "Game Over"}
                )
            print("sending state_change")
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "update",
                 "gid": self.game_id },
            )

        if content["method"] == "invite_bot":
            await self.channel_layer.send(
                "playdot-bot", {"type": "join.game", "data": {"gid": self.game_id}}
            )

    async def update(self, event):
        print("update method triggered")
        await self.send_json(
            {"method": "state_change", "data": {"gid": self.game_id}}
        )

def catch_integrity_error(fn):
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except IntegrityError:
            return (None, False)

    return inner


def do_turn(game, side, y, piece):
    game.do_move(side, int(y), piece)
