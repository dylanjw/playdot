#!/usr/bin/env python3

from django.db import models


class Board(models.Model):
    bid = models.UUIDField()
    last_to_play = models.CharField(max_length=1, null=True)
    width = models.IntegerField()


class Row(models.Model):
    board = models.ForeignKey(
        'Board',
        on_delete=models.CASCADE,
    )
    right_peak = models.IntegerField(null=True)
    left_peak = models.IntegerField(null=True)
    is_full = models.BooleanField(default=False)
    y = models.IntegerField()


class Space(models.Model):
    board = models.ForeignKey(
        'Board',
        on_delete=models.CASCADE,
    )
    row = models.ForeignKey(
        'Row',
        on_delete=models.CASCADE,
    )
    x = models.IntegerField()
    value = models.CharField(max_length=1)
