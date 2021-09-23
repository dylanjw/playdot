#!/usr/bin/env python3
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .board import Board, DjangoModelBackend
from .game import do_player_turn


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        move = text_data_json['move']
        player = text_data_json['player']
        bid = text_data_json['bid']
        side, row = move

        as_string = await database_sync_to_async(do_turn)(bid, player, side, row)

        await self.send(text_data=json.dumps({
            'as_string': as_string,
        }))


def do_turn(bid, player, side, row):
    b = Board(bid=bid, backend=DjangoModelBackend)
    do_player_turn(b, player, side, int(row))
    return str(b)
