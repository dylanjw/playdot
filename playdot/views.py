#!/usr/bin/env python3
from django.shortcuts import render
from . import game
from .board import Board, DjangoModelBackend


def index(request):
    return render(request, 'playdot/index.html')


def board(request, bid=None):
    if bid is None:
        b = Board(width=7, backend=DjangoModelBackend)
    else:
        b = Board(bid=bid, backend=DjangoModelBackend)
    board_data = {
        "bid": b.bid,
        "as_string": str(b),
    }
    return render(request, 'playdot/board.html', {"board_data": board_data})
