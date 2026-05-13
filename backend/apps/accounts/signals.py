from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import User


@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """Видаляємо старий аватар при заміні на новий"""
    if not instance.pk:
        return  # новий користувач — нічого не робимо

    try:
        old_instance = User.objects.get(pk=instance.pk)
        old_avatar = old_instance.avatar
    except User.DoesNotExist:
        return

    new_avatar = instance.avatar

    # Якщо аватар змінився і старий існує — видаляємо старий файл
    if old_avatar and old_avatar != new_avatar:
        if old_avatar.storage.exists(old_avatar.name):
            old_avatar.storage.delete(old_avatar.name)


@receiver(pre_delete, sender=User)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Видаляємо аватар при видаленні користувача"""
    if instance.avatar:
        if instance.avatar.storage.exists(instance.avatar.name):
            instance.avatar.storage.delete(instance.avatar.name)
