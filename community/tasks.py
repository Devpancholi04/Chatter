from .models import Community, CommunityMember, CommunityMessage,CommunityMessageReadReceipent

from django.core.cache import cache
from celery import shared_task
from django.contrib.auth import get_user_model
from datetime import datetime


user = get_user_model()

@shared_task
def notify_user(community_id, new_username):
    try:
        community = Community.objects.get(community_id = community_id)
        new_user = user.objects.get(username = new_username)
        message_time = datetime.now()
        get_system = user.objects.get(username = 'System')

        system_message = f"Hello {new_user.first_name} {new_user.last_name},\nWelcome to {community.community_name}"

        message = CommunityMessage.objects.create(
            community = community,
            sender = get_system,
            message = system_message,
        )

        member = CommunityMember.objects.filter(community = community).select_related('member')

        community_chat_history_key = f"COMMUNITY-CHAT-CACHE:{community_id}"
        list_messages = cache.get(community_chat_history_key, [])
        
        read_receiver = CommunityMessageReadReceipent.objects.filter(message=system_message, is_read = True).exclude(member__username = "System")
        readby = [receiver.member.username for receiver in read_receiver]

        list_messages.append({
            'message_id' : message.message_id,
            'community_id' : community_id,
            'community_name' : community.community_name,
            'sender_id' : message.sender.username,
            'received_id' : {
                'all_message_list' : [
                    members.member.username for members in community.community_members.all()
                    if members.member and members.member.username != "System"
                ],
            },
            'sender_name' : f"{message.sender.first_name}",
            'message' : system_message,
            'is_send' : True,
            'is_read' : CommunityMessageReadReceipent.objects.filter(message = system_message, member__username = "System", is_read = True).exists(),
            'readed_by' : readby,
            'date' : message.updated_at.strftime("%d-%m-%Y"),
            'time' : message.updated_at.strftime("%I:%M %p"),
        })

        for memb in member:
            if memb.member:
                cache_key = f"COMMUNITY-RECENT-KEY : {memb.member.uid} - {memb.member.username}"
                get_cache = cache.get(cache_key, [])

                for msg in get_cache:
                    if msg.get('community_id') == community_id:
                        msg['last_message'] = system_message
                        msg['last_msg_date'] = message_time.strftime('%d-%m-%Y')
                        msg['last_msg_time'] = message_time.strftime('%I:%M %p')
                        msg['unread_count'] += 1
                    else:
                        get_cache.append({
                            'community_id' : community_id,
                            'image_url' : community.image.url if community.image else '/media/images/user_logo/group_img.jpg',
                            'full_name' : community.community_name,
                            'last_message' : system_message,
                            'last_msg_date' : message_time.strftime('%d-%m-%Y'),
                            'last_msg_time' : message_time.strftime('%I:%M %p'),
                            'unread_count' : 1
                        })

                        cache.set(cache_key, get_cache, timeout=None)
        cache.set(community_chat_history_key, list_messages, timeout=None)
        
    except Exception as e:
        print(f"[celery task error] notify_user : {e}")