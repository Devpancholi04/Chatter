from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name="login"),
    path('register/', views.registration_page, name="register"),
    path('login/verify-otp/ref=<str:user_id>/<str:username>/', views.verify_otp, name="verify_otp"),
]