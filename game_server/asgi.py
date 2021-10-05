"""
ASGI config for game_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_server.settings')
asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter

import playdot.routing
from playdot.consumers import PlaydotBot


application = ProtocolTypeRouter({
  "http": asgi_app,
  "websocket": AuthMiddlewareStack(
         URLRouter(
             playdot.routing.websocket_urlpatterns
         )
     ),
  "channel": ChannelNameRouter(
      {
         "playdot-bot": PlaydotBot.as_asgi() 
      }
  )
 })
