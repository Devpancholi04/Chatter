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

from uuid import uuid4

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    async def connect(self):
        self.sender_uid = self.scope['url_route']['kwargs']['uid']
        self.sender_username = self.scope['url_route']['kwargs']['username']
        self.receiver_username = self.scope['url_route']['kwargs']['chat_username']
        
        user_ids = sorted([self.sender_username, self.receiver_username])
        room_id = "_".join(user_ids)
        self.room_group_name = f"chat_{room_id}"

        print(f"Connecting to room: {self.room_group_name}")

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
        message_time = datetime.now()
        
        sender_user, receiver_user = await self.get_user()
        message_id = self.gen.gen_mess_id()
        message_data = {
            'message_id' : message_id,
            'sender_id' : self.sender_username,
            'receiver_id' : self.receiver_username,
            'message' : data['message'],
            'is_send' : True,
            'is_read' : False,
            'date' : message_time.strftime("%d-%m-%Y"),
            'time' : message_time.strftime("%I:%M %p"),
        }

        message_data1 = {
            'message_id' : message_id,
            'sender_id' : self.sender_username,
            'receiver_id' : self.receiver_username,
            'message' : data['message'],
            'is_send' : False,
            'is_read' : False,
            'date' : message_time.strftime("%d-%m-%Y"),
            'time' : message_time.strftime("%I:%M %p"),
        }

        # print(sender_user.uid)
        cache_key = f"CHAT:CACHE:send-{sender_user.uid}-{sender_user.username} : rec:{receiver_user.uid}-{receiver_user.username}"
        cache_key1 = f"CHAT:CACHE:send-{receiver_user.uid}-{receiver_user.username} : rec:{sender_user.uid}-{sender_user.username}"

        buffer_key = f"CHAT:BUFFER:send-{sender_user.uid}-{sender_user.username} : rec:{receiver_user.uid}-{receiver_user.username}"
        buffer_key1 = f"CHAT:BUFFER:send-{receiver_user.uid}-{receiver_user.username} : rec:{sender_user.uid}-{sender_user.username}"
    
        get_cache = cache.get(cache_key, {})
        get_cache1 = cache.get(cache_key1, {})

        get_buffer = cache.get(buffer_key, {})
        get_buffer1 = cache.get(buffer_key1, {})

        new_mess = {f'{message_data['message_id']}' : message_data}
        new_mess1 = {f'{message_data['message_id']}' : message_data1}

        get_cache.update(new_mess)
        get_cache1.update(new_mess1)

        get_buffer.update(new_mess)
        get_buffer1.update(new_mess1)

        cache.set(cache_key, get_cache, timeout=None)
        cache.set(cache_key1, get_cache1, timeout=None)

        cache.set(buffer_key, get_buffer, timeout=None)
        cache.set(buffer_key1, get_buffer1, timeout=None)

        # print(f"get_cache_data : {get_cache}\n")
        # print(f"get_buffer_data : {get_buffer}\n")

        
        await self.channel_layer.group_send(
            self.room_group_name,{
                "type" : "chat_message",
                "message_id": message_data['message_id'],
                "sender_id" : message_data['sender_id'],
                "receiver_id" : message_data['receiver_id'],
                "message" : message_data['message'],
                'date' : message_data['date'],
                'time' : message_data['time']
            }
        )

    async def chat_message(self, event):
        current_username = self.sender_username  # This is the one who initiated the socket
        is_send = (event['sender_id'] == current_username)
        # print(is_send)
        await self.send(text_data=json.dumps({
            "message_id": event['message_id'],
            "sender_id": event['sender_id'],
            "receiver_id": event['receiver_id'],
            "message": event['message'],
            "date": event['date'],
            "time": event['time'],
            "is_send": is_send
        }))
