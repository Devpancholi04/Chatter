from channels.generic.websocket import AsyncWebsocketConsumer

import json

from account.models import CustomUser
from channels.db import database_sync_to_async
from .models import Group
from base.generate import generate_ids
from datetime import datetime

from django.core.cache import cache
from django.utils.text import slugify


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

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()    

    @database_sync_to_async
    def get_user(self):
        self.get_sender_user = CustomUser.objects.get(uid = self.sender_uid, username = self.sender_username)
        self.get_receiver_user = CustomUser.objects.get(username = self.receiver_username)

        return self.get_sender_user, self.get_receiver_user

    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(f"user_{self.sender_username}", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
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

        get_recent_cache_send = f"CHAT-RECENT-KEY: {sender_user.uid} - {sender_user.username}"
        get_recent_cache_rec = f"CHAT-RECENT-KEY: {receiver_user.uid} - {receiver_user.username}"

        get_recent_message_send = cache.get(get_recent_cache_send, [])
        get_recent_message_rece = cache.get(get_recent_cache_rec, [])

        
        for recent_msg in get_recent_message_send:
            if recent_msg.get('username') == receiver_user.username:
                recent_msg['last_message'] = data['message']
                recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                recent_msg['unread_count'] = 0

        for recent_msg in get_recent_message_rece:
            if recent_msg.get('username') == sender_user.username:
                recent_msg['last_message'] = data['message']
                recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                recent_msg['unread_count'] = recent_msg['unread_count'] + 1

        
        cache.set(cache_key, get_cache, timeout=None)
        cache.set(cache_key1, get_cache1, timeout=None)

        cache.set(buffer_key, get_buffer, timeout=None)
        cache.set(buffer_key1, get_buffer1, timeout=None)

        cache.set(get_recent_cache_send, get_recent_message_send, timeout=None)
        cache.set(get_recent_cache_rec, get_recent_message_rece, timeout=None)
        

        
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
        current_username = self.sender_username 
        is_send = (event['sender_id'] == current_username)
    
        await self.send(text_data=json.dumps({
            "message_id": event['message_id'],
            "sender_id": event['sender_id'],
            "receiver_id": event['receiver_id'],
            "message": event['message'],
            "date": event['date'],
            "time": event['time'],
            "is_send": is_send
        }))



class GroupConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['gid']
        self.group_name = self.scope['url_route']['kwargs']['gname']
        # self.group_name = slugify(self.group_name)
        self.sender_user = self.scope['user']

        self.room_group_name = f"chat_{self.group_id}_{self.group_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # await self.channel_later.group_add(f"Group_{self.room_group_name}", self.channel_name)

    @database_sync_to_async
    def get_users(self):
        get_group = Group.objects.get(group_id = self.group_id)
        get_all_user_in_group = list(get_group.members.all())
        return get_group, get_all_user_in_group

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_time = datetime.now()

        message_id = self.gen.gen_mess_id()
        group, members = await self.get_users()
        
        message_data = {
            'message_id' : message_id,
            'group_id' : self.group_id,
            'group' : self.group_name,
            'sender_id' : self.sender_user.username,
            'sender_name' : f"{self.sender_user.first_name} {self.sender_user.last_name}",
            'received_id' : {
                'all_member_list' : [member.username for member in members if member.username != self.sender_user.username],
            },
            'message' : data['message'],
            'is_group_message' : True,
            'is_read' : False,
            'readed_by' : [],
            'date' : message_time.strftime("%d-%m-%Y"),
            'time' : message_time.strftime("%I:%M %p"),
        }

        group_cache_key = f"GROUP-CHAT-CACHE:{self.group_id}"
        group_buffer_key = f"GROUP-CHAT-BUFFER:{self.group_id}"

        get_group_cache = cache.get(group_cache_key, [])
        get_buffer_cache = cache.get(group_buffer_key, [])

        sender_data = {**message_data, 'is_send': True}
        get_group_cache.append(sender_data)
        get_buffer_cache.append(sender_data)

        cache.set(group_cache_key, get_group_cache, timeout=None)
        cache.set(group_buffer_key, get_buffer_cache, timeout=None)

        get_recent_cache_send = f"CHAT-RECENT-KEY: {self.sender_user.uid} - {self.sender_user.username}"

        get_recent_message_send = cache.get(get_recent_cache_send, [])

        for recent_msg in get_recent_message_send:
            if recent_msg.get('group_id') == self.group_id:
                recent_msg['last_message'] = data['message']
                recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                recent_msg['unread_count'] = 0
        
        cache.set(get_recent_cache_send, get_recent_message_send, timeout=None)

        for member in members:
            if member.username != self.sender_user.username:
                get_recent_cache_rece = f"CHAT-RECENT-KEY: {member.uid} - {member.username}"

                get_recent_message_rece = cache.get(get_recent_cache_rece, [])

                for recent_msg in get_recent_message_rece:
                    if recent_msg.get('group_id') == self.group_id:
                        recent_msg['last_message'] = data['message']
                        recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                        recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                        recent_msg['unread_count'] = recent_msg['unread_count'] + 1

                cache.set(get_recent_cache_rece, get_recent_message_rece, timeout=None)

        await self.channel_layer.group_send(
            self.room_group_name,{
                "type" : "group_message",
                "message_id" : message_data['message'],
                "group_id" : message_data['group_id'],
                "group_name" : message_data['group'],
                "sender_id" : message_data['sender_id'],
                "receiver_id" : message_data['received_id'],
                "message" : message_data['message'],
                'date' : message_data['date'],
                'time' : message_data['time'],
            }
        )


    async def group_message(self, event):
        current_username = self.sender_user.username
        sender_name = f"{self.sender_user.first_name} {self.sender_user.last_name}"
        is_send = (event['sender_id'] == current_username)
        
        await self.send(text_data=json.dumps({
            "message_id" : event['message'],
            "group_id" : event['group_id'],
            "group_name" : event['group_name'],
            "sender_id" : event['sender_id'],
            "receiver_id" : event['receiver_id'],
            "message" : event['message'],
            'date' : event['date'],
            'time' : event['time'],
            'is_send' : is_send,
            'sender_name' : sender_name,
        }))