from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import CustomUser
from django.core.cache import cache

@receiver(post_migrate)
def create_user_group(sender, **kwargs):
    if not Group.objects.filter(name="ADMIN").exists():
        admin_group = Group.objects.create(name = "ADMIN")
        admin_group.permissions.set(Permission.objects.all())

    
    if not Group.objects.filter(name = "EMPLOYEE").exists():
        employee_group = Group.objects.create(name = "EMPLOYEE")
        employee_group.permissions.set(Permission.objects.filter(content_type__app_label = "account"))
    
    if not Group.objects.filter(name = "USER").exists():
        Group.objects.create(name = "USER")


@receiver(post_save, sender=CustomUser)
@receiver(post_delete, sender=CustomUser)
def delete_all_user_cache_data(sender, instance, **kwargs):
    cache.delete("ALL-USER-DATA-CACHE")