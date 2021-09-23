#!/usr/bin/env python3
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('board/', views.board, name='board'),
    path('board/<uuid:bid>/', views.board, name='board'),
]
