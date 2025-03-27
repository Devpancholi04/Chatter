from django.contrib import admin
from .models import *
# Register your models here.

class MessageAdmin(admin.ModelAdmin):
    search_fields = ['message_id','group__group_name','group__admin','group__group_id','sender__user_id', 'receiver__user_id', 'sender__first_name','receiver__first_name']
    list_filter = ['group','sender','receiver','is_read','is_edited','is_deleted','created_at','updated_at']
    readonly_fields = ('message_id','created_at','updated_at')

    fieldsets = (
        ("USER DETAILS", {'fields' : ('message_id','group','sender','receiver')}),
        ("MESSAGE & STATUS", {'fields' : ('message','is_group_message','is_read','is_edited','is_deleted')}),
        ("IMPORTANT DATES", {'fields' : ('created_at', 'updated_at')})
    )


class GroupAdmin(admin.ModelAdmin):
    search_fields = ['group_id','group_name','admin']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('group_id','created_at','updated_at')

    fieldsets = (
        ("GROUP DETAILS", {'fields': ('group_id','group_name','description','image')}),
        ("ADMIN & MEMBERs", {'fields' : ('admin','members')}),
        ("IMPORTANT DATES", {'fields' : ('created_at','updated_at')})
    )



admin.site.register(Message, MessageAdmin)
admin.site.register(Group, GroupAdmin)