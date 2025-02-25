from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('user_id', 'username','first_name', 'last_name','is_active','status','is_staff',)
    list_filter = ('gender','state','pin_code', 'status','is_anonymous_chat_enabled','roles','is_employee','is_staff','created_at','updated_at')
    search_fields = ('user_id','username','first_name','last_name','email','mobile_number','city','roles')
    ordering = ['-created_at']
    readonly_fields = ('uid','user_id','username','email_token','forget_token','created_at','updated_at')

    fieldsets = (
        ("User Unique Detials", {'fields' : ('uid','user_id','username','password')}),
        ("Basic Detials", {'fields' : ('first_name', 'last_name','email','mobile_number','dob','gender')}),
        ("Personal Profile Details", {'fields' : ('bio', 'profile_photos')}),
        ("Address Detials", {'fields' : ('address','city','state','pin_code')}),
        ("Account Status Details", {'fields' : ('status','is_active','is_two_step_verification','is_anonymous_chat_enabled')}),
        ("Roles & Permission Details", {'fields' : ('roles','is_employee','employee_verification','is_staff','is_superuser')}),
        ("Validation Tokens Detials", {'fields' : ('email_token','forget_token')}),
        ("Important Dates Detials", {'fields' : ('last_login','created_at','updated_at')})
    )
    add_fieldsets = (
        (None, {
            'classes' : ('wide',),
            'fields' : ('user_id','email','password1','password2','is_staff','is_active','is_superuser')
        }),
    )

    def get_readonly_fields(self, request, obj = None):
        if obj:
            return self.readonly_fields
        
        return ('user_id','created_at','updated_at')


admin.site.register(CustomUser,CustomUserAdmin)