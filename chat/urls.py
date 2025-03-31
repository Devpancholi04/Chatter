from django.urls import path
from . import views

urlpatterns = [
    path('<str:uid>/ref=<str:username>/', views.chat_page, name="chat_page"),
    
    path('load/history/sid=<str:uid>/sref=<str:username>/rid=<str:rec_uid>/rref=<str:rec_username>/', views.load_history, name="load_history"),
    path('api/recent-messages/<str:uid>/ref=<str:username>/', views.chat_page_sidebar, name='sidebar')
]   