from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from account.models import Friend
from chat.models import Group
from django.db.models import Q, Count
from community.models import Community, CommunityMember

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.hashers import check_password

from django.contrib import messages
from django.contrib.auth import logout

from base.otp import gen_otp
from base.emails import send_email
# Create your views here.

def home_page(request):
    user = request.user

    get_member_in_community = CommunityMember.objects.filter(member = user).values_list('community__community_id', flat=True)

    non_member_community = Community.objects.exclude(community_id__in=get_member_in_community)
    print(non_member_community)
    params = {
        'non_member_community' : non_member_community,
    }
    


    return render(request, "home/home_page.html", params) 

def profile_section(request):
    user = request.user

    friend = Friend.objects.filter(Q(sender = user) | Q(receiver = user), status='accepted')
    friend_count = friend.count()

    group = Group.objects.filter(members = user)
    
    get_community = CommunityMember.objects.filter(member = user)
    # print(get_community)
    

    params = {
        'user' : user,
        'friend_list' : friend,
        'friend_count' : friend_count,
        'group' : group,
        'community' : get_community,
    }
    return render(request, "home/profile.html", params)

def personal_details(request, uid):
    user = request.user
    changes_made = False
    login_required = False

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        bio = request.POST.get('bio')

        if first_name != user.first_name:
            user.first_name = first_name
            user.save()
            changes_made = True
        
        if last_name != user.last_name:
            user.last_name = last_name
            user.save()
            changes_made = True

        if email != user.email:
            user.email = email
            user.status = "INACTIVE"
            user.save()
            login_required = True
            changes_made = True
        
        if mobile_number != user.mobile_number:
            user.mobile_number = mobile_number
            user.save()
            changes_made = True

        if dob != user.dob:
            user.dob = dob
            user.save()
            changes_made = True
        
        if gender != user.gender:
            user.gender = gender
            user.save()
            changes_made = True

        if bio != user.bio:
            user.bio = bio
            user.save()
            changes_made = True

        if changes_made:
            messages.success(request, "Personal Detials Updated...")

            if login_required:
                messages.success(request, "Your email has been updated. Please Login again to verify your email.")
                logout(request)
                return redirect("login_page")
        else:
            messages.info(request, "No changes were made to your profile...") 

    return redirect('profile_page')


def address_details(request, uid):

    user = request.user
    changes_made = False

    if request.method == "POST":
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pin_code')

        if address != user.address:
            user.address = address
            user.save()
            changes_made = True
        
        if city != user.city:
            user.city = city
            user.save()
            changes_made = True
        
        if state != user.state:
            user.state = state
            user.save()
            changes_made = True
        
        if pincode != user.pin_code:
            user.pin_code = pincode
            user.save()
            changes_made = True

        if changes_made:
            messages.success(request, "Address Details updated Successfully")
    
    else:
        messages.warning(request, "No changes were made to your profile...")

    return redirect('profile_page')

@api_view(['POST'])
def update_profile_photo(request, uid):
    user = request.user
    if request.method == "POST":
        image = request.FILES.get('profile_photos')
        if image:
            user.profile_photos = image  # Assuming this is the correct field
            user.save()

            return Response({
                'message': 'Profile Photo has been updated',
                'url': user.profile_photos.url  # Return the image URL
            }, status=200)

    return Response({
        'message': 'Error while updating profile photo',
    }, status=400)

def deactivate_account(request, uid):

    user = request.user
    user_db_pass = user.password

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        check_pass = check_password(password, user_db_pass)

        if user.email != email:
            messages.warning(request, "Wrong mail id! Check Again...")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))            

        if check_pass != True:
            messages.warning(request, "Worng Password! Check Again..")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        otp = gen_otp()
        request.session[f"otp_{uid}_deactivate"] = otp

        subject = "Request for Account Deactivate"
        message = f'''Hello, {user.first_name},

This Email can Conatin some senstivite information 

It's Sad to here that you want to Deactivate your account.
Hope you will join us again in future.

Your One Time Password for account Deactivate is {otp}.
This Otp is valid for 5 min only.

Don't share OTP with anyone.
To Reactive your account Contact us.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team

'''
        send_email.delay(email = email, subject = subject, message = message)
        redirect('otp_verify_func', uid, type = "deactivate")

    return redirect('profile_page')

def change_password(request, uid):

    user = request.user
    user_db_pass = user.password
    email = user.email

    if request.method == "POST":
        old_pass = request.POST.get('old_pass')
        new_pass = request.POST.get('new_pass')
        confirm_pass = request.POST.get('co_new_pass')

        if new_pass != confirm_pass:
            messages.warning(request, "Check new password and Confirm password doesn't match")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        check = check_password(old_pass, user_db_pass)

        if check != True:
            messages.warning(request, "Worng Password! Check Again..")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        otp = gen_otp()
        request.session[f"otp_{uid}_change_password"] = otp
        request.session[f"new_pass_{uid}"] = new_pass

        subject = "Request For password change"
        message = f'''Hello {user.first_name},

This Email can Conatin some senstivite information

Your One Time Password for change password is {otp}.
This Otp is valid for 5 min only.

Don't share OTP with anyone.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
        
        send_email.delay(email = email, subject = subject, message = message)
        return redirect('otp_verify_func', uid, type = "change_password")

    
    return redirect("profile_page")

def two_f_a(request, uid):
    user = request.user
    email = user.email

    if request.method == "POST":
        twofa = request.POST.get("twofa")

        otp = gen_otp()
        request.session[f"otp_{uid}_2fa"] = otp
        request.session[f"twofa_{uid}"] = twofa

        if twofa == "on":
            subject = "Request to Activate Two Step verification"
            message = f'''Hello {user.first_name},

This Email can Conatin some senstivite information

Your One Time Password to Activate Two Step Verification is {otp}.
This Otp is valid for 5 min only.

Don't share OTP with anyone.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
        elif twofa == "off":
            subject = "Request to Deactivate Two Step verification"
            message = f'''Hello {user.first_name},

This Email can Conatin some senstivite information

Your One Time Password to Deactivate Two Step Verification is {otp}.
This Otp is valid for 5 min only.

Don't share OTP with anyone.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
        
        send_email.delay(email = email, subject = subject, message = message)
        return redirect('otp_verify_func', uid, type = "2fa")



    return redirect("profile_page")



def otp_verify(request, uid, type):
    user = request.user
    session_key = f"otp_{uid}_{type}"
    stored_otp = request.session.get(session_key)
    email = user.email

    if request.method == "POST":
        user_otp = request.POST.get('otp')

        if user_otp == str(stored_otp):
            if type == "deactivate":
                user.is_active = False
                user.save()

                subject = "Account Deactivated"
                message = f'''Hello {user.first_name},

on Your request your account has been Deactivated.
                
It's Sad to here that you want to Deactivate your account.
Hope you will join us again in future.

To reactivate your account. Contact us.

Byee,
Best Regards,
Chatter Team
'''
                send_email.delay(email=email, subject = subject, message = message)

                logout(request)
                messages.warning(request, "Your Account has been deactivate. To reactive Account Contact Us.")
                return redirect("login")

            elif type == "change_password":
                get_new_pass = request.session.get(f"new_pass_{uid}")
                user.set_password(get_new_pass)
                user.save()

                subject = "Password Changed Successfully"
                message = f'''Hello {user.first_name},

Hopefully its you {user.first_name} requested for reset password on chatter.

Your Login Password has been changed Successfully 

If not request by you can change the password by login on http://chatter.com:8000/accounts/login
or you can safely ignore this email.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
                send_email.delay(email=email, subject = subject, message = message)

                logout(request)
                messages.warning(request, "Your login password has been changed Successfully. Login Again.")
                return redirect("login")

            
            elif type == "2fa":
                get_status = request.session.get(f"twofa_{uid}")

                if get_status == "on":
                    user.is_two_step_verification = True
                    user.save()

                    subject = "Two Step Verification is On"
                    message = f'''Hello {user.first_name},

Congratulations your account has been now protected with Two Step Verification.  

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
                elif get_status == "off":
                    user.is_two_step_verification = False
                    user.save()

                    subject = "Two Step Verification is off"
                    message = f'''Hello {user.first_name},

your account is not longer protected with Two Step Verification.  

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Team
'''
                send_email.delay(email = email, subject = subject, message = message)
                return redirect("profile_page")

        else:
            messages.error(request, "Invalid OTP. Try again.")
            return redirect(request.META.get('HTTP_REFERER'))
            

    return render(request, 'accounts/two_step_verification.html')