#!/usr/bin/env python3
import json
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from . import models
from .game import Game


@require_GET
def index(request):
    return render(request, "playdot/index.html")


@require_POST
def create(request, width=7):
    game = Game(board_width=width)
    return JsonResponse(game.data.get_room_info())


@require_GET
def list_rooms(request):
    return JsonResponse(
        {
            "games": [
                game.get_room_info() for game in models.GameData.objects.all()
            ]
        }
    )


def game_state(request, gid):
    game = Game(gid=gid)
    return JsonResponse(game.as_dict())


@require_POST
def move(request, gid):
    game = Game(gid=gid)
    move_data = json.loads(request.body)
    print(f"move_data:{move_data}")
    game.do_move(move_data["side"], move_data["y"], move_data["player"])
    return HttpResponse("success")


@require_GET
def room(request, gid):
    return render(request, "playdot/room.html", {"room_data": {"gid": gid}})
