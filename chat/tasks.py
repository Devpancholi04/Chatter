import json
from datetime import datetime
from .models import Message, Group
from community.models import Community ,CommunityMessage, CommunityMessageReadReceipent

from django.core.cache import cache
from django.db import transaction
from django.contrib.auth import get_user_model

from django.db.models import Q
from celery import shared_task

user = get_user_model()

@shared_task
def flush_all_chats_buffer_to_db():
    pass


def flush_one_to_one_chats():
    buffer_keys = cache.keys("CHAT:BUFFER:*")
    print(buffer_keys)

    if not buffer_keys:
        return
    
    all_messages = []
    sorted_data = {}

    for keys in buffer_keys:
        messages_dict = cache.get(keys, {})

        # print(messages_dict)
        for msg_id, data in messages_dict.items():
            sorted_data[msg_id] = data

    
    # print(f"deduped data : {deduped}")

    for msg_id, msg in sorted_data.items():
        try:
            sender = user.objects.get(username = msg['sender_id'])
            receiver = user.objects.get(username = msg['receiver_id'])

            dt_str = f"{msg['date']} {msg['time']}"
            timestamp = datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")

            all_messages.append(Message(
                message_id = msg['message_id'],
                sender = sender,
                receiver = receiver,
                message = msg['message'],
                is_read = msg['is_read'],
                created_at = timestamp,
                updated_at = timestamp,
            ))

        except user.DoesNotExist as e:
            print(f"user not found : {e}")
        except Exception as e:
            print(f"error : {e}")

    
    print(f"final Result : {all_messages}")

    with transaction.atomic():
        Message.objects.bulk_create(all_messages)

    for keys in buffer_keys:
        cache.delete(keys)


def flush_group_chats():
    buffer_keys = cache.key("GROUP-CHAT-BUFFER:*")

    if not buffer_keys:
        return

    all_messages = []
    sorted_data = {}

    for key in buffer_keys:
        message = cache.get(key, [])
        
        for msg in message:
            sorted_data[msg['message_id']] = msg
    
    for msg_id, msg in sorted_data.items():
        try:
            sender = user.objects.get(username = msg['sender_id'])
            group = Group.objects.get(group_id = msg['group_id'])   
            
            dt_str = f"{msg['date']} {msg['time']}"
            timestamp = datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")

            all_messages.append(Message(
                message_id = msg['message_id'],
                group = group,
                sender = sender,
                message = msg['message'],
                is_group_message = True,
                created_at = timestamp,
                updated_at = timestamp,
            ))
        except user.DoesNotExist as e:
            print(f"user not found : {e}")
        except Exception as e:
            print(f"error : {e}")
    
    with transaction.atomic():
        Message.objects.bulk_create(all_messages)
    
    for keys in buffer_keys:
        cache.delete(keys)


def flush_community_chats():
    buffer_keys = cache.keys("COMMUNITY-CHAT-BUFFER:*")
    print("Flushing Community Chat:", buffer_keys)
    if not buffer_keys:
        return

    all_messages = []
    sorted_data = {}

    for key in buffer_keys:
        messages = cache.get(key, [])
        for msg in messages:
            sorted_data[msg['message_id']] = msg

    for msg_id, msg in sorted_data.items():
        try:
            sender = user.objects.get(username = msg['sender_id'])
            community = Community.objects.get(community_id = msg['community_id'])

            dt_str = f"{msg['date']} {msg['time']}"
            timestamp = datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")

            all_messages.append(CommunityMessage(
                message_id = msg['message_id'],
                community = community,
                sender = sender,
                message = msg['message'],
                created_at = timestamp,
                updated_at = timestamp,
            ))
        except user.DoesNotExist as e:
            print(f'User not found : {e}')
        except Exception as e:
            print(f"error : {e}")

    with transaction.atomic():
        CommunityMessage.objects.bulk_create(all_messages)

    
    for keys in buffer_keys:
        cache.delete(keys)


def update_marks_as_read_in_db():
    cache_keys = cache.Key("COMMUNITY-CHAT-CACHE:*")
    print("Upadting community chat as read......")

    if not cache_keys:
        return 
    
    new_messages = []
    sorted_data = {}

    for key in cache_keys:
        messages = cache.get(key, [])
        for msg in messages:
            sorted_data[msg['message_id']] = msg


    user_names = set([members for msg in sorted_data.values() for members in msg['received_id']['all_message_list']])
    users = user.objects.filter(username__in=user_names)
    user_dict = {user.username: user for user in users}

    for msg_id, msg in sorted_data.items():
        try:
            get_message = CommunityMessage.objects.get(message_id = msg['message_id'])

            for members in msg['received_id']['all_message_list']:
                user_instance = user_dict.get(members)
                if not user_instance:
                    print(f"User {members} not found")
                    continue

                exisitng_message = CommunityMessageReadReceipent.objects.filter(
                    Q(member = user_instance) &
                    Q(message = get_message) &
                    Q(is_read = True)
                ).exists()

                if not exisitng_message:
                    new_messages.append(CommunityMessageReadReceipent(
                        member = user_instance,
                        message = get_message,
                        is_read = True
                    ))
        except user.DoesNotExist as e:
            print(f"User not found : {e}")
        except CommunityMessage.DoesNotExist as e:
            print(f"Message Not Found : {e}")
        except Exception as e:
            print(f"Error : {e}")
    
    with transaction.atomic():
        if new_messages:
            CommunityMessageReadReceipent.objects.bulk_create(new_messages)
    