from django.db import models
from uuid import uuid4
from base.generate import generate_ids
from account.models import CustomUser
# Create your models here.

    

class Group(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    group_id = models.CharField(max_length=50, primary_key=True, editable=False)
    group_name = models.CharField(max_length=50)

    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='group/group_logos/', null=True, blank=True)

    admin = models.ForeignKey(CustomUser, related_name="group_admin", on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name="group")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.group_id:
            self.group_id = self.gen.gen_group_id(self.group_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.group_name


    
class Message(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    message_id = models.CharField(max_length=100, primary_key=True, editable=False)
    group = models.ForeignKey(Group, models.SET_NULL, null=True, blank=True)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="send_message")
    receiver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_message")
    message = models.TextField()

    is_group_message = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = self.gen.gen_mess_id()
        super().save(*args,**kwargs)

    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        name = [f"chat from {self.sender} to {self.receiver}" if self.is_group_message == False else f"{self.sender} in {self.group.group_name} - {self.receiver}"]
        return name[0]
