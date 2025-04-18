from django.shortcuts import render
from account.models import CustomUser
from .models import AIChat
# Create your views here.

def ai_chat_page(request):

    return render(request, "ai/ai_chat_page.html")