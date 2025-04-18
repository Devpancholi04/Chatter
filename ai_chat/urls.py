from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.ai_chat_page, name="ai_chat_page"),
]