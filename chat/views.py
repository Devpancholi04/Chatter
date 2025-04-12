from django.shortcuts import render
from django.http import JsonResponse
from .models import *

from django.utils import timezone

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

from django.contrib.auth.decorators import login_required

# rest
from django.shortcuts import get_object_or_404
from account.models import CustomUser
from django.db.models import Count, Max, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
from datetime import datetime
# Create your views here.

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

def chat_page(request, uid, username):

    
    parmas = {'uid' : uid, 'username' : username}
    return render(request, "chat/chat_page.html", parmas)


@api_view(['GET'])
def chat_page_sidebar(request, uid, username):
    user = get_object_or_404(CustomUser, uid=uid, username=username)
    # print(f"User : {user.username}")

    chat_recent_key = f"CHAT-RECENT-KEY: {uid} - {username}"
    recent_message = cache.get(chat_recent_key)

    # print(f"recentdatarecent_message)
    # if get_recent_message:
    print(f"from cahce : {recent_message}")
    if not recent_message:
        chats = Message.objects.filter(Q(sender=user) | Q(receiver=user) | Q(group__members = user))
    
        chat_users = {}
        groups = {}
    
        for chat in chats:
            if chat.is_group_message and chat.group:
                if chat.group.group_id not in groups:
                    last_message = Message.objects.filter(group = chat.group).order_by('-updated_at').first()
                    unread_count = Message.objects.filter(group = chat.group, is_read = False).count()

                    groups[chat.group.group_id] = {
                        'group_id' : chat.group.group_id,
                        'image_url' : chat.group.image.url if chat.group.image else '/media/images/user_logo/group_img.jpg',
                        'full_name' : chat.group.group_name,
                        'last_message' : last_message.message if last_message else '',
                        'last_msg_date' : last_message.updated_at.strftime('%d-%m-%Y') if last_message else '',
                        'last_msg_time' : last_message.updated_at.strftime('%I:%M %p') if last_message else '',
                        'unread_count' : unread_count 
                    }
            else:
                chat_user = chat.sender if chat.sender != user else chat.receiver
        
                if chat_user.uid not in chat_users:
                    last_message = Message.objects.filter(
                        (Q(sender=chat_user, receiver=user) | Q(sender=user, receiver=chat_user))
                    ).order_by('-updated_at').first()
            
                    unread_count = Message.objects.filter(
                        sender=chat_user, receiver=user, is_read=False
                    ).count()
            
                    chat_users[chat_user.uid] = {
                        'uid': chat_user.uid,
                        'image_url' : chat_user.profile_photos.url if chat_user.profile_photos else '/media/images/user_logo/user_img.jpg',
                        'full_name': f"{chat_user.first_name} {chat_user.last_name}",
                        'username': chat_user.username,
                        'last_message': last_message.message if last_message else '',
                        'last_msg_date' : last_message.updated_at.strftime('%d-%m-%Y') if last_message else '',
                        'last_msg_time': last_message.updated_at.strftime('%I:%M %p') if last_message else '',
                        'unread_count': unread_count
                    }

        recent_message_chat_list = list(chat_users.values())
        recent_message_group_list = list(groups.values())
        
        combined_list = recent_message_chat_list + recent_message_group_list

        def get_datetime(chat):
            dt_str = f"{chat['last_msg_date']} {chat['last_msg_time']}"
            print(dt_str)
            # return datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
            try:
                return datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
            except ValueError:
                return datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")
        

        recent_message = sorted(combined_list, key=get_datetime, reverse=True)
        print(f"recent message : {recent_message}")
        cache.set(chat_recent_key, recent_message, timeout=DEFAULT_TIMEOUT)
    
    return Response({'message': recent_message})


@api_view(['GET'])
def load_history(request, uid, username, rec_uid, rec_username):

    chat_cache_id = f"CHAT:CACHE:send-{uid}-{username} : rec:{rec_uid}-{rec_username}"

    list_messages = cache.get(chat_cache_id)
    print(f"from cache data : ",list_messages)
    list_messages_data = {}

    if not list_messages:
        list_messages = Message.objects.filter(
            (Q(sender__uid = uid, sender__username=username, receiver__uid = rec_uid, receiver__username=rec_username) | Q(sender__uid = rec_uid, sender__username =rec_username, receiver__uid = uid, receiver__username = username))
        ).values().order_by('updated_at')
        
        for val in list_messages:
            list_messages_data[val['message_id']] = {
                'message_id' : val['message_id'],
                'sender_id' : val['sender_id'],
                'receiver_id' : val['receiver_id'],
                'message' : val['message'],
                'is_send' : True if val['sender_id'] == username else False,
                'is_read' : val['is_read'],
                'date' : val['updated_at'].strftime("%d- %m-%Y"),
                'time' : val['updated_at'].strftime("%I:%M %p"),
            }
        list_messages = list_messages_data
        
        cache.set(chat_cache_id, list_messages_data, timeout=CACHE_TTL)

    return Response({'Messages' : list_messages})


@api_view(['GET'])
def load_group_history(request, group_id, uid, username):
    print(username)
    group_chat_history_id = f"GROUP-CHAT-CACHE:{group_id} - {uid}"
    list_messages = cache.get(group_chat_history_id)

    if not list_messages:
        try:
            get_group = Group.objects.get(group_id = group_id)
        except Group.DoesNotExist:
            return Response({'error': 'Group does not exist'}, status=404)
        
        messages = Message.objects.filter(group = get_group, is_group_message=True).order_by('updated_at')

        list_messages = [
            {
                'message_id' : msg.message_id,
                'sender_id' : msg.sender.username,
                'received_id' : {
                    'all_member_list' : [member.username for member in get_group.members.all()],
                },
                'sender_name' : f"{msg.sender.first_name} {msg.sender.last_name}",
                'message' : msg.message,    
                'is_send' : True if msg.sender.username == username else False,
                'is_read' : msg.is_read,
                'date' : msg.updated_at.strftime("%d-%m-%Y"),
                'time' : msg.updated_at.strftime("%I:%M %p"),
            }
            for msg in messages
        ]
            
        cache.set(group_chat_history_id, list_messages, timeout=CACHE_TTL)

    return Response({'Messages' : list_messages})

   

@api_view(['GET'])
def mark_as_read(request, uid, username, rec_uid, rec_username):
    chat_cache_id = f"CHAT:CACHE:send-{uid}-{username} : rec:{rec_uid}-{rec_username}"
    chat_buffer_id = f"CHAT:BUFFER:send-{uid}-{username} : rec:{rec_uid}-{rec_username}"

    recent_cache_message1 = f"CHAT-RECENT-KEY: {uid} - {username}"
    recent_cache_message2 = f"CHAT-RECENT-KEY: {rec_uid} - {rec_username}"


    get_cache_data = cache.get(chat_cache_id, {})
    get_buffer_data = cache.get(chat_buffer_id, {})

    get_recent_msg_data1 = cache.get(recent_cache_message1, [])
    get_recent_msg_data2 = cache.get(recent_cache_message2, [])

    if not get_cache_data:
        load_message_api = f"http://127.0.0.1:8000/chats/api/load/one-2-one/chats/history/sid={uid}/sref={username}/rid={rec_uid}/rref={rec_username}/"
        response = requests.get(load_message_api)
        get_cache_data = cache.get(chat_cache_id, {})
        get_buffer_data = cache.get(chat_buffer_id, {})

    # print(f"\nBefore Cache update : {get_cache_data}\n")
    # print(f"Before Buffer update : {get_buffer_data}\n")

    updated_count = 0

    new_cache_data = {}
    for msg_id, msg_data in get_cache_data.items():
        if msg_data['receiver_id'] ==username and msg_data['is_read'] == False:
            print(msg_data['receiver_id'])
            print(msg_data['is_read'])
            msg_data['is_read'] = True
            updated_count += 1
        new_cache_data[msg_id] = msg_data

    new_buffer_data = {}
    for msg_id, msg_data in get_buffer_data.items():
        if msg_data['receiver_id'] == username and not msg_data['is_read']:
            msg_data['is_read'] = True
        new_buffer_data[msg_id] = msg_data

    for msg_data in get_recent_msg_data1:
        if msg_data.get('username') == rec_username and msg_data.get('unread_count',0) > 0:
            msg_data['unread_count'] = 0

    for msg_data in get_recent_msg_data2:
        if msg_data.get('username') == username and msg_data.get('unread_count',0) > 0:
            msg_data['unread_count'] = 0

    # print(f"After cache update : {new_cache_data}\n")
    # print(f"After buffer update : {new_buffer_data}\n")

    cache.set(chat_cache_id, new_cache_data, timeout=None)
    cache.set(chat_buffer_id, new_buffer_data, timeout=None)

    cache.set(recent_cache_message1, get_recent_msg_data1, timeout=None)
    cache.set(recent_cache_message2, get_recent_msg_data2, timeout=None)

    return Response({
        'message': 'All messages marked as read.',
        'total_updated': updated_count
    })

