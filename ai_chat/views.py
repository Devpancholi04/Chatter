from django.shortcuts import render
from account.models import CustomUser
from django.contrib.auth.decorators import login_required
from .models import AIChat
# Create your views here.

@login_required(login_url='/accounts/login/')
def ai_chat_page(request):

    return render(request, "ai/ai_chat_page.html")