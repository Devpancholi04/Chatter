from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home_page(request):
    # /media/images/user_logo/user_img.jpg
    return render(request, "home/home_page.html")