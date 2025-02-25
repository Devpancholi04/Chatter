from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from uuid import uuid4
from base.generate import generate_ids

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self,username, email, password = None, **extra_fields):

        if not email:
            raise ValueError("The Email field cannot be Empty!!")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self,username, email, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("The Admin must have is_staff = True")
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("The Admin must have is_superuser = True")
        

        return self.create_user(username, email, password, **extra_fields)
    


class CustomUser(AbstractBaseUser, PermissionsMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    STATUS_CHOICE = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    GENDER_CHOICES = [
        ("M",'M'),
        ("F", 'F'),
        ("T",'T'),
        ("NOT PREFER TO SAY", "Not Prefer to Say"),
    ]

    ROLES_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
        ('USER', 'User'),
    ]

    VERIFICATION_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]


    uid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user_id = models.CharField(max_length=100, editable=False, unique=True)
    username = models.CharField(max_length=100, editable=False, primary_key=True)

    # user basic details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES, null=True, blank=True)

    # user Profile Detials
    bio = models.TextField(null=True, blank=True)
    profile_photos = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    # Address detials
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)

    # Account status
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="INACTIVE", help_text="This indicated the user is verified")
    is_active = models.BooleanField(default=True, help_text="This indicated the user is Active")
    is_two_step_verification = models.BooleanField(default=False)
    is_anonymous_chat_enabled = models.BooleanField(default=False)

    # Roles & Permission
    roles = models.CharField(max_length=20, choices=ROLES_CHOICES, default='USER')

    is_employee = models.BooleanField(default=False, help_text="This indicated the user is employee and has only employee rights")
    employee_verification =  models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='PENDING')
    is_staff = models.BooleanField(default=False, help_text="This indicated the user is employee and Admin")
    is_superuser = models.BooleanField(default=False, help_text = "This indicated the user is Admin")
    

    # Tokens
    email_token = models.CharField(max_length=100, null=True, blank=True, editable=False)
    forget_token = models.CharField(max_length=100, null=True, blank=True, editable=False)


    #important Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','mobile_number','first_name','last_name']

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.gen.gen_user_id(self.first_name)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name} -- {self.username}"