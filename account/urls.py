from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('register/', views.registration_page, name="register"),
    path('login/verifyotp/ref=<str:user_id>/id=<str:username>/', views.verify_otp, name="verify_otp"),
]