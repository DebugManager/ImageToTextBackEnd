from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from main.consumers import FirstConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', FirstConsumer.as_asgi()),
    # Add more routing for different consumers if needed
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})