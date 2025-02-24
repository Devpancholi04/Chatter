from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@receiver(post_migrate)
def create_user_group(sender, **kwargs):
    if not Group.objects.filter(name="ADMIN").exists():
        admin_group = Group.objects.create(name = "ADMIN")
        admin_group.permissions.set(Permission.objects.all())

    
    if not Group.objects.filter(name = "EMPLOYEE").exists():
        employee_group = Group.objects.create(name = "EMPLOYEE")
        employee_group.permissions.set(Permission.objects.filter(ContentType__app_label = "account"))
    
    if not Group.objects.filter(name = "USER").exists():
        Group.objects.create(name = "USER")