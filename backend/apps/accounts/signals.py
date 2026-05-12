from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import User


def _delete_file(field):
    if field and field.name:
        try:
            field.storage.delete(field.name)
        except Exception:
            pass


@receiver(pre_save, sender=User)
def user_avatar_on_update(sender, instance, **kwargs):
    """Видаляє старий аватар якщо юзер завантажив новий"""
    if not instance.pk:
        return
    try:
        old = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    if old.avatar and old.avatar != instance.avatar:
        _delete_file(old.avatar)


@receiver(post_delete, sender=User)
def user_avatar_on_delete(sender, instance, **kwargs):
    _delete_file(instance.avatar)
