from django.shortcuts import render
from .models import *

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

from django.contrib.auth.decorators import login_required

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
                'image_url' : community.image.url if community.image else '/media/iamges/user_logo/group_img.jpg',
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