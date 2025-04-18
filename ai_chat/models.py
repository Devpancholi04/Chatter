from django.db import models
from account.models import CustomUser
from base.generate import generate_ids
# Create your models here.

class AIChat(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    ai_message_id = models.CharField(max_length=50, primary_key=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ai_chats")
    ai_model = models.CharField(max_length=200, choices=[
        ('DeepSeek-Paid', 'DEEPSEEK-R1:paid'),
        ('DeepSeek-Free', 'deepseek-r1-distill-llama-70b:free'),
        ('QWEN', 'QWEN-32b:free'),
    ])
    api_used = models.CharField(max_length=200)
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.ai_message_id:
            self.ai_message_id = self.gen.gen_ai_chat_message_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"AI Chat by {self.user.username} using {self.ai_model}"
    
