from channels.generic.websocket import AsyncWebsocketConsumer

import json
from account.models import CustomUser
from .models import AIChat
from channels.db import database_sync_to_async
from base.generate import generate_ids
from openai import OpenAI
import random
import asyncio
import re


class AIConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    async def connect(self):
        self.sender_user = self.scope['user']

        self.room_ai_chat = "AI_Chat_Connected"
        await self.channel_layer.group_add(self.room_ai_chat, self.channel_name)
        await self.accept()

    async def disconnect(self, closeCode):
        await self.channel_layer.group_discard(self.room_ai_chat, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.get_ai_response(message)

    
    
    api1 = "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"
    api2 = "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"

    api = [api1, api2]
    ai_model = {
        # 'general' : ('deepseek/deepseek-r1', 'DEEPSEEK-R1:paid'),
        'general' : ('deepseek/deepseek-r1-zero:free', 'deepseek-r1-distill-llama-70b:free'),
        'programming' : ('qwen/qwq-32b:free','QWEN-32b:free')
    }

    programming_keyword = [
        "python", "java", "javascript", "code", "function", "bug", "error",
        "how to write", "program", "algorithm", "logic", "html", "css", "api",
        "terminal", "database", "sql", "backend", "frontend", "compile", "run",
        "wap","write a program",'kotlin','c#','.net',
    ]

    def is_programming_related(self, text):
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.programming_keyword)
    
    async def get_ai_response(self, text):

        is_code_query = self.is_programming_related(text)
        category = "programming" if is_code_query else "general"

        model_slug, model_name = self.ai_model[category]

        for key in self.api:
            try:
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=key
                )

                response = client.chat.completions.create(
                    model = model_slug,
                    messages = [
                        {
                            "role" : "system",
                            "content" : "You are useful AI Assistant and always and reply in English."
                        },
                        {
                            "role" : "user", 
                            "content" : text
                        }
                    ],
                    stream=True
                )

                full_response = ""

                for mess in response:
                    if mess.choices[0].delta.content:
                        chunk = mess.choices[0].delta.content
                        full_response += chunk
                        # print(chunk, end="", flush=True)
                        await asyncio.sleep(0.01)
                
                full_respone = re.sub(r"\*\*|###", "", full_response)
                full_respone = f"$$ {full_respone.strip()} $$"


                await self.send(text_data=json.dumps({
                    'message': full_response,
                    'streaming' : True
                }))

                ai_chat_id = self.gen.gen_ai_chat_message_id()
                user = await database_sync_to_async(
                lambda: CustomUser.objects.get(username=self.sender_user.username)
                )()

                if user:
                    await database_sync_to_async(
                        lambda: AIChat.objects.create(
                            ai_message_id=ai_chat_id,
                            user=user,
                            ai_model=model_name,
                            api_used=key,
                            user_message=text,
                            ai_response=full_response
                        )
                    )()

                return
            except Exception as e:
                print(f"[{model_name}] failed with the key {key} : {e}")
                continue
        
        await self.send(text_data=json.dumps({
            'message': "⚠️ All AI agents are currently unavailable. Please try again later.",
            'model': "None"
        }))

    