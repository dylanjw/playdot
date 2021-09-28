#!/usr/bin/env python3
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .game import Game, PlaydotPiece, RowFull, GameOver
from .models import ChannelPlayer, Piece
from django.db import IntegrityError


class GameConsumer(AsyncJsonWebsocketConsumer):
    game = None

    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["gid"]
        self.game = await database_sync_to_async(Game)(gid=self.game_id)
        self.group_name = "playdot_%s" % self.game_id

        # Join room group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        for piece in (PlaydotPiece.ONE, PlaydotPiece.TWO):
            print(f"checking piece for assignment: {piece}")
            p_instance, _ = await database_sync_to_async(
                Piece.objects.get_or_create
            )(value=piece.value)

            player, created = await database_sync_to_async(
                catch_integrity_error(ChannelPlayer.objects.get_or_create)
            )(
                game=self.game.data,
                playing_as=p_instance,
                channel_name=self.channel_name,
            )
            print(f"obj:{player}, create?:{created}")
            # either found or added to db
            if created or (player is not None and not created):
                self.player = piece
                break
        else:
            self.player = "observer"
        print(f"sending player assignment: {piece.value}")
        await self.send_json({"method": "assign_player", "data": piece.value})

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
                {"type": "update"},
            )

    async def update(self, event):
        print("update method triggered")
        await self.send_json({"method": "state_change", "data": ""})


def catch_integrity_error(fn):
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except IntegrityError:
            return (None, False)

    return inner


def do_turn(game, side, y, piece):
    game.do_move(side, int(y), piece)
