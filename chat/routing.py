from django.urls import re_path
from .consumers import  ChatConsumer, GroupConsumer


websocket_urlpatterns = [
    # re_path(r"ws/load/chats/(?P<uid>[0-9a-fA-F-]+)/(?P<username>[\w.@+-]+)/$", LoadChatConsumer.as_asgi())
    re_path(r"ws/chats/(?P<uid>[0-9a-fA-F-]+)/(?P<username>[\w.@+-]+)/(?P<chat_username>\w+)/$",ChatConsumer.as_asgi()),
    # re_path(r"ws/group/chats/(?P<gid>[0-9a-fA-F-]+)/(?P<gname>[\w.@+-]+)/$", GroupConsumer.as_asgi()),
    re_path(r"ws/group/chats/(?P<gid>[0-9a-zA-Z-]+)/(?P<gname>[\w.@+\- %]+)/$", GroupConsumer.as_asgi()),

]