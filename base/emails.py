from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task


# this function is used for the account activation email
@shared_task
def account_activation_email(name, email, email_token):
    subject = "Account Activation Requireds"
    email_from = settings.EMAIL_HOST_USER
    message = f'''Hello {name},

Click on the Link to activate your Account http://chatter.com:8000/accounts/activate/{email_token}/

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Teams
'''
    
    send_mail(subject, message, email_from, [email])


#this function is used for the reset password email purpose
@shared_task
def reset_password_request_email(name, email, forget_token):
    subject = "Reset Password Request"
    email_from = settings.EMAIL_HOST_USER
    message = f'''Hello {name},

Hopefully its you {name} requested for reset password on chatter.
Click on the below Link to reset login password.

http://chatter.com:8000/accounts/password-reset/confirm/{forget_token}/ 

If not request by you can change the password by login on chatter.com:8000 
or you can safely ignore this email.

Don't replay to this mail.
This is auto generated mail.

Best Regards,
Chatter Teams
'''
    
    send_mail(subject, message, email_from, [email])


# this function is used to send any email that are required in the main code.
@shared_task
def send_email(email, subject, message, **kwargs):

    email_from = settings.EMAIL_HOST_USER

    send_mail(subject, message, email_from, [email])