#!/usr/bin/env python3
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('board/create/<int:width>', views.create, name='create'),
    path('list/', views.list_rooms, name='list_rooms'),
    path('board/<uuid:gid>/', views.game_state, name='game'),
    path('board/<uuid:gid>/move', views.move, name='move')
]
