from django.shortcuts import render, redirect

from .models import CustomUser
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
import uuid
from base.emails import account_activation_email, send_email
from base.otp import gen_otp
from datetime import datetime
from django.contrib.auth.models import User, Group

# Create your views here.

def login_page(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.warning(request, "Required email and password")
            return HttpResponseRedirect(request.path_info)

        try:
            get_user = CustomUser.objects.get(email = email)

            auth_user = authenticate(email = email, password = password)

            if auth_user:
                user = get_user

                login(request, auth_user)

                if user.status == "INACTIVE":
                    email_token = str(uuid.uuid4())
                    user.email_token = email_token
                    user.save()

                    account_activation_email.delay(email = user.email, name=user.first_name, email_token = email)
                    messages.warning(request, "Email Not Verified! Link Send on registered Email..")
                    return HttpResponseRedirect(request.path_info)
                
                if user.is_two_step_verification == True:
                    user_id = user.user_id
                    otp = gen_otp()
                    request.session[user_id] = otp

                    subject = "Login OTP verification"
                    message = f'''Hello, {user.first_name}, 

This Email can contain some senstivite information
                    
Your One Time Password for login is {otp}.
This Otp is valid for 5 min only.

Don't share OTP with anyone.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''               
                    send_email.delay()(subject=subject, message=message, email=user.email)
                    return HttpResponse(request, "<h1> Login Success </h1>") # otp verification link will come here.
                
                # sending login email to the user if not activated two step verification mail

                subject = "Login Attempt"
                message = f'''Hello {user.first_name},

New Login Attempt at {datetime.now().strftime('%d-%m-Y %H:%M:%S')}

if not attempt login by you. Change the password as soon as possbile.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
                send_email.delay(subject=subject, message=message, email=user.email)
                return HttpResponse(request, "<h1> Login Success </h1>") # add the login of the home page after login to be redirect user

                     

        except CustomUser.DoesNotExist():
            messages.warning(request, "user not found!")
            return HttpResponseRedirect(request.path_info)
        

    return render(request, 'accounts/login.html')



def registration_page(request):



    return render(request, 'accounts/register.html')