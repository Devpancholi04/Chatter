from django.shortcuts import render
from .models import *

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

from django.contrib.auth.decorators import login_required
from .tasks import notify_user
#rest
from django.shortcuts import get_object_or_404
from account.models import CustomUser
from django.db.models import Q, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import datetime
# Create your views here.

def community_page(request, uid, username):

    
    parmas = {'uid' : uid, 'username' : username}
    return render(request, "community/community_page.html", parmas)

@api_view(['GET'])
def community_page_sidebar(request, uid, username):
    user = get_object_or_404(CustomUser, uid=uid, username=username)
        
    community_recent_key = f"COMMUNITY-RECENT-KEY : {uid} - {username}"
    recent_message = cache.get(community_recent_key, [])
    # print(f"recent_message : {recent_message}\n")

    def get_datetime(chat):
        dt_str = f"{chat['last_msg_date']} {chat['last_msg_time']}"
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            return datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")


    if not recent_message:
        get_user_in_communities = CommunityMember.objects.filter(member = user).select_related('community')
    
        print(get_user_in_communities)
        community_data = []
        for membership in get_user_in_communities:
            community = membership.community
            print(f"Community name : {community}")
            last_message = CommunityMessage.objects.filter(community = community).order_by('-updated_at').first()

            unread_count = CommunityMessage.objects.filter(
                community = community
            ).exclude(
                read_recipent__member = user
            ).exclude(
                sender = user
            ).count()

            print(f"last_message : {last_message}")
            print(f"count : {unread_count}")

            community_data.append({
                'community_id' : community.community_id,
                'image_url' : community.image.url if community.image else '/media/images/user_logo/group_img.jpg',
                'full_name' : community.community_name,
                'last_message' : last_message.message if last_message else '',
                'last_msg_date' : last_message.updated_at.strftime("%d-%m-%Y") if last_message else '',
                'last_msg_time' : last_message.updated_at.strftime("%I:%M %p") if last_message else '',
                'unread_count' : unread_count,
            })
        # print(f"data  : {community_data}\n")
        recent_message = sorted(community_data, key=get_datetime, reverse=True)
        # print(f"data from db  : {recent_message}\n")
        cache.set(community_recent_key, recent_message, timeout=None)
    else:
        recent_message = sorted(recent_message, key=get_datetime, reverse=False)
        # print(f"data from cache  : {recent_message}\n")

    return Response({'message' : recent_message})


@api_view(['GET'])
def load_community_messages(request, cid, uid, username):

    community_chat_history_key = f"COMMUNITY-CHAT-CACHE:{cid}"
    list_messages = cache.get(community_chat_history_key, [])

    if list_messages:
        for item in list_messages:
            item['is_send'] = item['sender_id'] == username

    else:
        try:
            get_community = Community.objects.get(community_id = cid)
        except Community.DoesNotExist:
            return Response({'error' : "Community Does not Exists"}, status=404)
        
        messages = CommunityMessage.objects.filter(community = get_community).order_by('updated_at')
        list_messages = []

        for msg in messages:
            read_receiver = CommunityMessageReadReceipent.objects.filter(message=msg, is_read = True).exclude(member__username = username)
            readby = [receiver.member.username for receiver in read_receiver]

            list_messages.append({
                'message_id' : msg.message_id,
                'community_id' : cid,
                'community_name' : msg.community.community_name,
                'sender_id' : msg.sender.username,
                'received_id' : {
                    'all_message_list' : [
                        member.member.username for member in get_community.community_members.all()
                        if member.member and member.member.username != username
                    ],
                },
                'sender_name' : f"{msg.sender.first_name} {msg.sender.last_name}",
                'message' : msg.message,
                'is_send' : True if msg.sender.username == username else False,
                'is_read' : CommunityMessageReadReceipent.objects.filter(message=msg, member__username = username, is_read=True).exists(),
                'readed_by' : readby,
                'date' : msg.updated_at.strftime("%d-%m-%Y"),
                'time' : msg.updated_at.strftime("%I:%M %p"),
            })

        cache.set(community_chat_history_key, list_messages, timeout=None)

    return Response({'message' : list_messages})


@api_view(['GET'])
def community_message_marks_as_read(request, cid, uid, username):

    community_cache_key = f"COMMUNITY-CHAT-CACHE:{cid}"
    community_buffer_key = f"COMMUNITY-CHAT-BUFFER:{cid}"

    get_community_cache = cache.get(community_cache_key, [])
    get_community_buffer = cache.get(community_buffer_key, [])

    newly_read_msgs = []

    for chat in get_community_cache:
        # if username in chat['received_id']['all_member_list'] and username not in chat['readed_by']:
        if(
            isinstance(chat.get('received_id'), dict) and
            username in chat['received_id'].get('all_member_list',[]) and
            username not in chat.get('readed_by', [])
        ):
            chat['readed_by'].append(username)
            newly_read_msgs.append(chat)

    for chat in get_community_buffer:
        if(
            isinstance(chat.get('received_id'), dict) and
            username in chat['received_id'].get('all_member_list',[]) and
            username not in chat.get('readed_by', [])
        ):
            chat['readed_by'].append(username)
            newly_read_msgs.append(chat)
        # if username in chat['received_id']['all_member_list'] and username not in chat['readed_by']:

    cache.set(community_cache_key, get_community_cache, timeout=None)
    cache.set(community_buffer_key, get_community_buffer, timeout=None)

    community_recent_key = f"COMMUNITY-RECENT-KEY : {uid} - {username}"
    recent_message = cache.get(community_recent_key, [])

    for chats in recent_message:
        if chats.get('community_id') == cid:
            chats['unread_count'] = 0
    
    cache.set(community_recent_key, recent_message, timeout=None)

    return Response({"message": "All Community Messages marked as read",})

@api_view(['GET'])
def join_community(request, username, community_id):
    user = get_object_or_404(CustomUser, username=username)
    community = get_object_or_404(Community, community_id = community_id)

    if CommunityMember.objects.filter(member=user, community = community).exists():
        return Response({
            "message" : f"{username} is already in {community.community_id}"
        }, status=400)
    
    created = CommunityMember.objects.create(member = user, community = community)
    if created:
        notify_user.delay(community_id, username)

    return Response({
        "message" : f"{username} added to {community.community_name}"
    })