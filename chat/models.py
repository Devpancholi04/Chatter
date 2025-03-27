from django.db import models
from uuid import uuid4
from base.generate import generate_ids
from account.models import CustomUser
# Create your models here.

class DirectMessage(models.Model):
    message_id = models.CharField(max_length=100, primary_key=True, editable=False)
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="send_message")
    receiver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_message")
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = generate_ids.gen_mess_id()
        super().save(*args,**kwargs)
    
    def __str__(self):
        return f"Chat from {self.sender} to {self.receiver}"