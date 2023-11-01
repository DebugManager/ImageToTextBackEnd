from django.urls import re_path

from main.consumers import NewConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', NewConsumer.as_asgi()),
    # Add more routing for different consumers if needed
]