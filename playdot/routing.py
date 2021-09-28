#!/usr/bin/env python3

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(r"ws/playdot/<uuid:gid>/", consumers.GameConsumer.as_asgi()),
]
