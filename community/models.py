from django.db import models
from base.generate import generate_ids
from account.models import CustomUser
# Create your models here.
 
class Community(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    community_id = models.CharField(max_length=50, primary_key=True, editable=False)
    community_name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/community/community_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.community_id:
            self.community_id = self.gen.gen_community_id(self.community_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.community_name} created on {self.created_at} is Active {self.is_active}"


class CommunityMember(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, related_name='community_members', null=True)
    joined_on = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('member','community')

    def __str__(self):
        return f"{self.member.username} in {self.community.community_name}"
    
class CommunityMessage(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen = generate_ids()

    message_id = models.CharField(max_length=50, primary_key=True, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="community_messages")
    message = models.TextField()
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = self.gen.gen_community_message_id()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.community.community_name}"
    

class CommunityMessageReadReceipent(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="community_reads")
    message = models.ForeignKey(CommunityMessage, on_delete=models.CASCADE, related_name="read_recipent")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member','message')

    def __str__(self):
        return f"{self.member.username} readed message {self.message.message_id} at {self.read_at}"