from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.registration_page, name="register"),

    path('login/', views.login_page, name="login"),
    path('ref<str:user_id>/activate/tk=<str:email_token>/', views.activate_account, name="activate_account"),
    path('login/verifyotp/ref=<str:user_id>/id=<str:username>/', views.verify_otp, name="verify_otp"),

    path('login/resetpassword/', views.reset_password, name="reset_password"),
    path('password-reset/ref=<str:user_id>/confirm/tk=<str:forget_token>/', views.change_password, name="change_password"),

    path('logout/', views.logout_page, name='logout_page')
]