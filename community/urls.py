from django.urls import path
from . import views

urlpatterns = [
    path('chats/<str:uid>/ref=<str:username>/', views.community_page, name="community_page"),

    path('api/recent-messages/<str:uid>/ref=<str:username>/', views.community_page_sidebar, name='community_sidebar'),

    path('api/load/message/history/cid=<str:cid>/ref=<str:uid>/refu=<str:username>/', views.load_community_messages, name="load_community_messages"),

    path('api/mark-as-read/messages/cid=<str:cid>/uid=<str:uid>/username=<str:username>/', views.community_message_marks_as_read, name="community_message_marks_as_read"),
]