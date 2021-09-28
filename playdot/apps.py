from django.apps import AppConfig


class PlaydotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "playdot"

    def ready(self):
        from .models import ChannelPlayer

        ChannelPlayer.objects.all().delete()
