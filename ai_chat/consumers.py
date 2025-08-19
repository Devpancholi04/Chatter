from channels.generic.websocket import AsyncWebsocketConsumer

import json
from account.models import CustomUser
from .models import AIChat
from channels.db import database_sync_to_async
from base.generate import generate_ids
from openai import OpenAI
import asyncio
import re

import os
from dotenv import load_dotenv

load_dotenv()


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

    
    
    api1 = os.getenv('api1')
    api2 = os.getenv('api2')

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

    predefined_response = {
        "what is chatter ai?" : "Chatter AI is a smart assistant that helps you to get instant answers to your queries!",
        "who created you?" : "I was created by the amazing **Dev Pancholi** and **Garv Bhatia**",
        "who is dev pancholi?" : "**Dev Pancholi** is a full stack developer who created me(Chatter) with garv bhatia. And worked as front-end development, backend development, Database Mangement, etc.",
        "who is garv bhatia?" : "**Garv Bhatia** is a FrontEnd Developed who created me with Dev Pancholi. And worked as FrontEnd Developer.",
        "how to use chatter ai?" : "Just type your question and press send! I’ll take care of the rest.", 

        "are you human?": "Nope! I'm a virtual assistant designed to help you as best as I can.",
        "what is your name?": "I’m Chatter AI, your personal assistant powered by Dev Pancholi and Grav Bhatia",
        "can you help me?": "Of course! Ask me anything and I’ll do my best to assist you.",
        "what can you do?": "I can answer questions, help you with programming, give suggestions, and more!",
        "how do you work?": "I use advanced AI models to understand your question and respond intelligently.",
        
        "tell me a joke": "Why don’t programmers like nature? It has too many bugs! 🐛",
        "are you smart?": "I try to be! My creator Dev Pancholi trained me with a lot of brainy stuff.",
        "do you sleep?": "Nope, I'm always online... 24/7 for you!",    
        "do you have emotions?": "Not really, but I can pretend pretty well 😉",
        "who is your crush?": "Probably Siri... but don’t tell Alexa! 🤫",

        "what is python?": "Python is a high-level, interpreted programming language known for its simplicity.",
        "what is an api?": "An API is a set of rules that allows one software app to interact with another.",
        "what is machine learning?": "Machine Learning is a way for computers to learn from data without being explicitly programmed.",
        "what is git?": "Git is a version control system that helps developers track and manage changes in code.",
        "what is a database?": "A database is a structured collection of data stored electronically for easy access and management.",
        

        "how to stay motivated?": "Set small goals, reward yourself, and remember why you started. You got this! 💪",
        "how to focus on study?": "Try the Pomodoro technique, keep distractions away, and stay consistent.",
        "tips to be productive?": "Make a to-do list, prioritize tasks, and avoid multitasking.",
        "how to deal with failure?": "Failure is part of the journey. Learn, improve, and come back stronger!",
        "give me a motivational quote": "Believe you can and you're halfway there. -Theodore Roosevelt",

    }

    def is_programming_related(self, text):
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.programming_keyword)
    
    async def get_ai_response(self, text):
        normalized_text = text.strip().lower()

        if normalized_text in self.predefined_response:
            cached_response = self.predefined_response[normalized_text]
            await self.send(text_data=json.dumps({
                'message': cached_response,
                'streaming': True
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
                        ai_model="Cached",
                        api_used="None",
                        user_message=text,
                        ai_response=cached_response
                    )
                )()
            return


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

                print(full_respone)

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

    