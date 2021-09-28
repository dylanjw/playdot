#!/usr/bin/env python3

from django.db import models
from .constants import PlaydotPiece


class ChannelPlayer(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game", "playing_as"], name="player_constraint"
            )
        ]

    game = models.ForeignKey(
        "GameData",
        on_delete=models.CASCADE,
    )
    channel_name = models.CharField(max_length=200)
    playing_as = models.ForeignKey(
        "Piece", on_delete=models.CASCADE, related_name="players"
    )


class GameData(models.Model):
    gid = models.UUIDField()
    winner = models.ForeignKey(
        "Piece",
        on_delete=models.SET_NULL,
        related_name="games_winning_in",
        null=True,
    )
    next_to_play = models.ForeignKey(
        "Piece",
        on_delete=models.SET_NULL,
        related_name="games_next_in",
        null=True,
    )
    board = models.OneToOneField(
        "GridBoard", on_delete=models.CASCADE, related_name="game"
    )
    meta = models.JSONField(null=True)

    def get_room_info(self):
        return {"gid": self.gid, "board_width": self.board.width}


class PlaydotGameData(GameData):
    @classmethod
    def new(cls, gid, board_width):
        for piece in PlaydotPiece:
            if not Piece.objects.filter(value=piece.value).exists():
                Piece(value=piece.value).save()
        if not cls.objects.filter(gid=gid).exists():
            grid_board = GridBoard(width=board_width)
            grid_board.save()
            game_data = cls(
                gid=gid,
                board=grid_board,
                next_to_play=Piece.objects.get(value=PlaydotPiece.ONE.value),
            )
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
        return space.value.value

    def set_piece(self, x, y, value):
        print(f"Setting piece: x:{x}, y:{y}, value{value}")
        try:
            row = Row.objects.get(board=self, y=y)
        except Row.DoesNotExist:
            row = Row(board=self, y=y)
            row.save()
        try:
            piece = Piece.objects.get(value=value)
        except Piece.DoesNotExist:
            piece = Piece(value=value)
            piece.save()
        try:
            space = Space.objects.get(board=self, row=row, x=x)
            space.value = piece
        except Space.DoesNotExist:
            space = Space(board=self, row=row, x=x, value=piece)
        space.save()


class Row(models.Model):
    board = models.ForeignKey(
        "GridBoard",
        on_delete=models.CASCADE,
        related_name="rows",
    )
    y = models.IntegerField()

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Row indices must be integers")
        row = Space.objects.get(row=self, x=index)
        return row


class Space(models.Model):
    board = models.ForeignKey(
        "GridBoard", on_delete=models.CASCADE, related_name="spaces"
    )
    row = models.ForeignKey(
        "Row", on_delete=models.CASCADE, related_name="spaces"
    )
    x = models.IntegerField()
    value = models.ForeignKey(
        "Piece", on_delete=models.CASCADE, related_name="spaces"
    )
