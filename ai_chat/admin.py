from django.contrib import admin
from .models import AIChat
# Register your models here.

class AIChatAdmin(admin.ModelAdmin):
    search_fields = ['ai_message_id','user__username','ai_model']
    list_filter = ['ai_model','created_at','updated_at']
    readonly_fields = ('ai_message_id','created_at','updated_at')

    fieldsets = (
        ("AI CHATS DETAILS", {"fields" : ('ai_message_id','user')}),
        ("AI MODELS & RESPONSE", {"fields" : ('ai_model','user_message','ai_response')}),
        ("IMPORTANT DATES", {"fields" : ('created_at','updated_at')})
    )

admin.site.register(AIChat, AIChatAdmin)