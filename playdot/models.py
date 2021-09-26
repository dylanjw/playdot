#!/usr/bin/env python3

from django.db import models


class GameData(models.Model):
    gid = models.UUIDField()
    next_to_play = models.ForeignKey(
        "Piece",
        on_delete=models.SET_NULL,
        related_name="games_next_in",
        null=True
    )
    board = models.OneToOneField(
        'GridBoard',
        on_delete=models.CASCADE,
        related_name='game'
    )
    meta = models.JSONField(null=True)

    def get_room_info(self):
        return {"gid": self.gid, "board_width": self.board.width}


class PlaydotGameData(GameData):
    @classmethod
    def new(cls, gid, board_width):
        if not cls.objects.filter(gid=gid).exists():
            grid_board = GridBoard(width=board_width)
            grid_board.save()
            game_data = cls(gid=gid, board=grid_board)
            game_data.save()
            return game_data
        return cls.objects.get(gid=gid)


class Piece(models.Model):
    value = models.IntegerField()


class GridBoard(models.Model):

    width = models.IntegerField()

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("GridBoard indices must be integers")
        row = Row.objects.get(board=self, y=index)
        return row

    def get_piece(self, x, y):
        try:
            row = Row.objects.get(board=self, y=y)
            space = Space.objects.get(board=self, row=row, x=x)
        except (Row.DoesNotExist, Space.DoesNotExist):
            return 0
        return space.value

    def set_piece(self, x, y, value):
        try:
            row = Row.objects.get(board=self, y=y)
        except Row.DoesNotExist:
            row = Row(board=self, y=y)
            row.save()
        try:
            space = Space.objects.get(board=self, row=row, x=x)
            piece = Piece.objects.get(value=value)
            space.value = piece
        except Space.DoesNotExist:
            space = Space(board=self, row=row, x=x, value=value)
        except Piece.DoesNotExist:
            piece = Piece(value=value)
            piece.save()
            space.value = piece
        space.save()


class Row(models.Model):
    board = models.ForeignKey(
        'GridBoard',
        on_delete=models.CASCADE,
        related_name="rows",
    )
    right_peak = models.IntegerField(null=True)
    left_peak = models.IntegerField(null=True)
    is_full = models.BooleanField(default=False)
    y = models.IntegerField()

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Row indices must be integers")
        row = Space.objects.get(row=self, x=index)
        return row


class Space(models.Model):
    board = models.ForeignKey(
        'GridBoard',
        on_delete=models.CASCADE,
        related_name="spaces"
    )
    row = models.ForeignKey(
        'Row',
        on_delete=models.CASCADE,
        related_name="spaces"
    )
    x = models.IntegerField()
    value = models.CharField(max_length=1)
