from django.urls import re_path
from .consumers import CommunityConsumer

websocket_urlpatterns = [
    re_path(r"ws/community/chats/(?P<cid>[0-9a-zA-Z\-]+)/(?P<communityName>[\w.@+\- %]+)/$", CommunityConsumer.as_asgi()),
]