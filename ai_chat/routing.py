from django.urls import re_path
from .consumers import AIConsumer

websocket_urlpatterns = [
    re_path(r"ws/AI/chats/$", AIConsumer.as_asgi()),
]