from django.urls import path
from . import views

urlpatterns = [
    path('<str:uid>/ref=<str:username>/', views.chat_page, name="chat_page"),
    
    path('api/load/one-2-one/chats/history/sid=<str:uid>/sref=<str:username>/rid=<str:rec_uid>/rref=<str:rec_username>/', views.load_history, name="load_history"),
    path('api/load/group/chats/history/gid=<str:group_id>/ref=<str:uid>/refu=<str:username>/', views.load_group_history, name="load_group_history"),

    path('api/recent-messages/<str:uid>/ref=<str:username>/', views.chat_page_sidebar, name='sidebar'),

    path('api/mark-as-read/sid=<str:uid>/sref=<str:username>/rid=<str:rec_uid>/rref=<str:rec_username>/', views.mark_as_read, name='make_as_read'),
    path('api/group/chats/mark-as-read/gid=<str:group_id>/uid=<str:uid>/username=<str:username>/', views.group_message_mark_as_read, name="group_message_mark_as_read"),
]   
