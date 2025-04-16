from django.contrib import admin
from .models import *
# Register your models here.

class CommunityAdmin(admin.ModelAdmin):
    search_fields = ['community_id','community_id']
    list_filter = ['created_at','updated_at','is_active']
    readonly_fields = ('community_id','updated_at','created_at')

    fieldsets = (
        ("COMMUNITY DETAILS", {'fields' : ('community_id','community_name')}),
        ("COMMUNITY DESC", {'fields' : ('description','image','is_active')}),
        ("IMPORTANT DATES", {'fields' : ('created_at', 'updated_at')})
    )

class CommunityMemberAdmin(admin.ModelAdmin):
    search_fields = ['member__username','community__community_id','community__community_name']
    list_filter = ['member__username','community__community_name','joined_on']
    readonly_fields = ('joined_on',)

    fieldsets = (
        ("COMMUNITY MEMBERS DETAILS", {'fields' : ('member','community')}),
        ("IMPORTANT DATES", {'fields' : ('joined_on',)}),
    )

class CommunityMessageAdmin(admin.ModelAdmin):
    search_fields = ['message_id','community__community_id','community__community_name','sender__username']
    list_filter = ['sender','community__community_name','is_edited','is_deleted']
    readonly_fields = ('message_id','created_at','updated_at')

    fieldsets = (
        ("MESSAGE DETAILS", {'fields' : ('message_id', 'community',)}),
        ("SENDER & MESSAGE DETAILS", {'fields' : ('sender','message','is_edited','is_deleted')}),
        ("IMPORTANT DATES", {'fields' : ('created_at','updated_at')}),
    )
    

class CommunityMessageReadReceipentAdmin(admin.ModelAdmin):
    search_fields = ['member__username','message__message_id']
    list_filter = ['member__username','message__community__community_name']
    readonly_fields = ('read_at',)


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityMember, CommunityMemberAdmin)
admin.site.register(CommunityMessage, CommunityMessageAdmin)
admin.site.register(CommunityMessageReadReceipent, CommunityMessageReadReceipentAdmin)