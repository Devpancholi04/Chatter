from django.contrib import admin
from .models import *
# Register your models here.

class DirectMessageAdmin(admin.ModelAdmin):
    search_fields = ['message_id', 'sender__user_id', 'receiver__user_id', 'sender__first_name','receiver__first_name']
    list_filter = ['sender','receiver','is_read','is_edited','is_deleted','created_at','updated_at']
    readonly_fields = ('message_id','created_at','updated_at')

    fieldsets = (
        ("USER DETAILS", {'fields' : ('message_id','sender','receiver')}),
        ("MESSAGE & STATUS", {'fields' : ('message','is_read','is_edited','is_deleted')}),
        ("IMPORTANT DATES", {'fields' : ('created_at', 'updated_at')})
    )



admin.site.register(DirectMessage, DirectMessageAdmin)