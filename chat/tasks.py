import json
from datetime import datetime
from .models import Message

from django.core.cache import cache
from django.db import transaction
from django.contrib.auth import get_user_model

from celery import shared_task

user = get_user_model()

@shared_task
def flush_all_chats_from_buffer_to_db():
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

        