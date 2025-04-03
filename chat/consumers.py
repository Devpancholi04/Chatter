from channels.generic.websocket import AsyncWebsocketConsumer
import re
import asyncio
import json
from django.contrib.auth.models import AnonymousUser
# from .utils import get_recent_chats
from asgiref.sync import sync_to_async
from .models import Message
from account.models import CustomUser
from channels.db import database_sync_to_async
from django.core.cache import cache
from base.generate import generate_ids
from datetime import datetime

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    async def connect(self):
        self.sender_uid = self.scope['url_route']['kwargs']['uid']
        self.sender_username = self.scope['url_route']['kwargs']['username']
        self.receiver_username = self.scope['url_route']['kwargs']['chat_username']

        self.room_group_name = f"chat_{self.sender_uid}_{self.sender_username}_{self.receiver_username}" 

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()    

    @database_sync_to_async
    def get_user(self):
        self.get_sender_user = CustomUser.objects.get(uid = self.sender_uid, username = self.sender_username)
        self.get_receiver_user = CustomUser.objects.get(username = self.receiver_username)

        return self.get_sender_user, self.get_receiver_user

    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message_time = date = datetime.now()
        
        sender_user, receiver_user = await self.get_user()

        message_data = {
            'message_id' : self.gen.gen_mess_id(),
            'sender_id' : self.sender_username,
            'receiver_id' : self.receiver_username,
            'message' : data['message'],
            'is_send' : True,
            'is_read' : True,
            'date' : message_time.strftime("%d-%m-%Y"),
            'time' : message_time.strftime("%I:%M %p"),
        }
        # print(sender_user.uid)
        cache_key = f"CHAT:CACHE:send-{sender_user.uid}-{sender_user.username} : rec:{receiver_user.uid}-{receiver_user.username}"
        buffer_key = f"CHAT:BUFFER:send-{sender_user.uid}-{sender_user.username} : rec:{receiver_user.uid}-{receiver_user.username}"
    
        get_cache = cache.get(cache_key, {})
        get_buffer = cache.get(buffer_key, {})

        new_mess = {f'{message_data['message_id']}' : message_data}

        get_cache.update(new_mess)
        get_buffer.update(new_mess)

        cache.set(cache_key, get_cache, timeout=None)
        cache.set(buffer_key, get_buffer, timeout=None)

        print(f"get_cache_data : {get_cache}\n")
        print(f"get_buffer_data : {get_buffer}\n")

        
        await self.channel_layer.group_send(
            self.sender_username,{
                "type" : "chat_message",
                "sender_id" : message_data['sender_id'],
                "receiver_id" : message_data['receiver_id'],
                "message" : message_data['message'],
                'date' : message_data['date'],
                'time' : message_data['time']
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))