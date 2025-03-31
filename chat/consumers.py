from channels.generic.websocket import AsyncWebsocketConsumer
import re
import asyncio
import json
from django.contrib.auth.models import AnonymousUser
# from .utils import get_recent_chats
from asgiref.sync import sync_to_async
from .models import Message
from account.models import CustomUser
from django.core.cache import cache


class LoadChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def chat_message(self, event):
        pass