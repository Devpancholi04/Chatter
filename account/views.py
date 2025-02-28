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

# importing redis cache functionality
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
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
                    return redirect('login', user.uid, user.username) # otp verification link will come here.
                
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
    
    # getting the data from cache
    all_user_data_cache_key = "ALL-USER-DATA-CACHE"
    get_all_user_data = cache.get(all_user_data_cache_key)

    # if data is not in the cache setting the data in the cache
    if not get_all_user_data:
        get_all_user_data = CustomUser.objects.all()
        cache.set(all_user_data_cache_key, list(get_all_user_data), timeout=CACHE_TTL)

    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')

        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        repassword = request.POST.get('re-password')


        # check if user name already used or not
        if username in [user.username for user in get_all_user_data ]:
            messages.warning(request, "username already taken!")
            return HttpResponseRedirect(request.path_info) 
        
        # check if email is already used or not
        if email in [user.email for user in get_all_user_data]:
            messages.warning(request, "Email already taken!")
            return HttpResponseRedirect(request.path_info)
        
        # check if mobile is already used or not
        if mobile in [user.mobile_number for user in get_all_user_data ]:
            messages.warning(request, "Mobile Number is already taken!")
            return HttpResponseRedirect(request.path_info)

        # check password match or not
        if password != repassword:
            messages.warning(request, "Password Doesn't match!")
            return HttpResponseRedirect(request.path_info)
        

        # creating account and sending account active email

        email_token = str(uuid.uuid4())
        user_obj = CustomUser.objects.create(
            username = username,
            first_name = fname,
            last_name = lname,
            email = email,
            mobile_number = mobile,
            dob = dob,
            gender = gender,
            email_token = email_token
        ) 
        user_obj.set_password(password)
        user_group = Group.objects.get(name = "USER")
        user_obj.groups.add(user_group)
        user_obj.save()

        # sending welcome message
        subject = "Account Created Successfully"
        message = f'''Hello {fname},

Welcome to chatter.com:8000,

Your account has been created successfully. 

you will shortly recieve in account activation email.
Activate your account as soon as possible to start.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''       
        
        send_email.delay(email = email, subject = subject, message = message)

        # sending account activation email to the user
        account_activation_email.delay(email = email, name = fname, email_token = email_token)
        messages.success(request, "Registation Success.Verify the email and login. Check mail")
        return redirect('login')
    
    return render(request, 'accounts/register.html')


def verify_otp(request, user_id, username):

    # getting the data from cache
    all_user_data_cache_key = "ALL-USER-DATA-CACHE"
    get_all_user_data = cache.get(all_user_data_cache_key)

    # if data is not in the cache setting the data in the cache
    if not get_all_user_data:
        get_all_user_data = CustomUser.objects.all()
        cache.set(all_user_data_cache_key, list(get_all_user_data), timeout=CACHE_TTL)


    # checking the user
    try:
        user = next((user_data for user_data in get_all_user_data if str(user_data.uid) == user_id), None)
    
        
        if request.method == "POST":
            user_otp = request.POST.get('otp')
            session_otp = request.session.get(user_id)

            if session_otp == user_otp:
                del request.session[user_id]

                return redirect() #redirect to home page
        
            else:
                messages.warning(request, "Invalid OTP.")
                return HttpResponseRedirect(request.path_info)
    
    except user.DoesNotExist():
        messages.warning(request, "Invalid username")
        return redirect('login')

    return render(request, 'accounts/two_step_verification.html')