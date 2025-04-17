from channels.generic.websocket import AsyncWebsocketConsumer

import json

from account.models import CustomUser
from .models import *
from channels.db import database_sync_to_async
from datetime import datetime

from django.core.cache import cache


class CommunityConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    async def connect(self):
        self.community_id = self.scope['url_route']['kwargs']['cid']
        self.community_name = self.scope['url_route']['kwargs']['communityName']

        self.sender_user = self.scope['user']

        if not self.sender_user:
            return

        self.room_community_name = f"community_{self.community_id}_{self.community_name}"
        await self.channel_layer.group_add(self.room_community_name, self.channel_name)
        await self.accept() 


    @database_sync_to_async
    def get_user(self):
        get_community = Community.objects.get(community_id = self.community_id)
        # sender_user_obj = CustomUser.objects.get(username = self.sender_user)
        get_members_in_community = CommunityMember.objects.filter(community = get_community)
        get_all_user_in_community = [cm.member for cm in get_members_in_community]
        return get_community, get_all_user_in_community

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_community_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_time = datetime.now()

        message_id = self.gen.gen_community_message_id()
        community,members = await self.get_user()

        message_data = {
            'message_id' : message_id,
            'community_id' : self.community_id,
            'community_name' : self.community_name,
            'sender_id' : self.sender_user.username,
            'received_id' : {
                'all_message_list' : [member.username for member in members if member.username != self.sender_user.username]
            },
            'sender_name' : f"{self.sender_user.first_name} {self.sender_user.last_name}",
            'message' : data['message'],
            'is_read' : False,
            'readed_by' : [],
            'date' : message_time.strftime("%d-%m-%Y"),
            'time' : message_time.strftime("%I:%M %p"),
        }

        community_cache_key = f"COMMUNITY-CHAT-CACHE:{self.community_id}"
        community_buffer_key = f"COMMUNITY-CHAT-BUFFER:{self.community_id}"

        get_community_cache = cache.get(community_cache_key, [])
        get_community_buffer = cache.get(community_buffer_key, [])

        sender_data = {**message_data, 'is_send' : True}

        get_community_cache.append(sender_data)
        get_community_buffer.append(sender_data)

        cache.set(community_cache_key, get_community_cache, timeout=None)
        cache.set(community_buffer_key, get_community_buffer, timeout=None)

        get_recent_community_cache_send = f"COMMUNITY-RECENT-KEY : {self.sender_user.uid} - {self.sender_user.username}"

        get_recent_message_send = cache.get(get_recent_community_cache_send, [])

        for recent_msg in get_recent_message_send:
            if recent_msg.get('community_id') == self.community_id:
                recent_msg['last_message'] = data['message']
                recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                recent_msg['unread_count'] = 0
        
        cache.set(get_recent_community_cache_send, get_recent_message_send, timeout=None)

        for member in members:
            if member.username != self.sender_user.username:
                get_recent_cache_rece = f"COMMUNITY-RECENT-KEY : {member.uid} - {member.username}"

                get_recent_message_rece = cache.get(get_recent_cache_rece, [])
                
                for recent_msg in get_recent_message_rece:
                    if recent_msg.get('group_id') == self.group_id:
                        recent_msg['last_message'] = data['message']
                        recent_msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                        recent_msg['last_msg_time'] = message_time.strftime("%I:%M %p")
                        recent_msg['unread_count'] = recent_msg['unread_count'] + 1

                cache.set(get_recent_cache_rece, get_recent_message_rece, timeout=None)

        await self.channel_layer.group_send(
            self.room_community_name,{
                "type" : "community_message",
                "message_id" : message_data['message_id'],
                "community_id" : message_data['community_id'],
                "community_name" : message_data['community_name'],
                "sender_id" : message_data['sender_id'],
                "sender_name" : message_data['sender_name'],
                "receiver_id" : message_data['received_id'],
                "message" : message_data['message'],
                'date' : message_data['date'],
                'time' : message_data['time'],
            }
        )

    async def community_message(self, event):
        current_username = self.sender_user.username
        is_send = (event['sender_id'] == current_username)

        await self.send(text_data=json.dumps({
            "message_id" : event['message_id'],
            "community_id" : event['community_id'],
            "community_name" : event['community_name'],
            "sender" : event['sender_id'],
            "sender_name" : event['sender_name'],
            "receiver_id" : event['receiver_id'],
            "message" : event["message"],
            'date' : event['date'],
            'time' : event['time'],
            'is_send' : is_send,
        }))