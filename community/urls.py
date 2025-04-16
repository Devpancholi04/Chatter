from django.urls import path
from . import views

urlpatterns = [
    path('chats/<str:uid>/ref=<str:username>/', views.community_page, name="community_page"),

    path('api/recent-messages/<str:uid>/ref=<str:username>/', views.community_page_sidebar, name='community_sidebar'),

]