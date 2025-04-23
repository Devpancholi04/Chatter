from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('home/profile/', views.profile_section, name="profile_page"),

    path('api/update/personal/details/<str:uid>/', views.personal_details, name='personal_details'),
    path('api/update/address/details/<str:uid>/', views.address_details, name="address_details"),
    path('api/update/profile-photos/<str:uid>/', views.update_profile_photo, name="update_photo"),
    path('api/deactivate/account/<str:uid>/', views.deactivate_account, name="deactivate_account"),
    path('api/change-password/<str:uid>/', views.change_password, name="change_password"),
    path('api/active/two-f-a/verification/<str:uid>', views.two_f_a, name="two_f_a"),
    path('verify/otp/page/<str:uid>/type=<str:type>/', views.otp_verify, name="otp_verify_func")
]