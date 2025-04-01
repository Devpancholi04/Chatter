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
    
    # if get_recent_message:
    #     print(f"from cahce : {get_recent_message}")
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
                        'last_msg_time': last_message.updated_at.strftime('%I:%M %p') if last_message else '',
                        'unread_count': unread_count
                    }

        recent_message_chat_list = list(chat_users.values())
        recent_message_group_list = list(groups.values())
        
        combined_list = recent_message_chat_list + recent_message_group_list

        recent_message = sorted(combined_list, key=lambda x:x['last_msg_time'])
        print(f"recent message : {recent_message}")
        cache.set(chat_recent_key, recent_message, timeout=DEFAULT_TIMEOUT)
    
    return Response({'message': recent_message})



def load_history(request, uid, username, rec_uid, rec_username):

    chat_cache_id = f"CHAT:CACHE:send{uid}-{username} : rec:{rec_uid}-{rec_username}"
    chat_buffer_id = f"CHAT:CACHE:send{uid}-{username} : rec:{rec_uid}-{rec_username}"

    get_messages = cache.get(chat_cache_id)

    if not get_messages:
        get_messages = Message.objects.filter(sender__uid = uid, sender__username=username, receiver__uid = rec_uid, receiver__username=rec_username).values()
        # print("data from db")
        cache.set(chat_cache_id, list(get_messages), timeout=CACHE_TTL)

    print(get_messages)

    return JsonResponse({'Messages' : list(get_messages)}, safe=False)