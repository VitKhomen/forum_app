from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post
from .models import Post, PostImages, PostVideo


@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def invalidate_posts_cache(sender, instance, **kwargs):
    # Збираємо всі можливі ключі і видаляємо
    sorts = ['hot', 'views', 'likes', 'comments']
    cats = ['', instance.category.slug if instance.category else '']

    for sort in sorts:
        for cat in cats:
            # Видаляємо перші 10 offset-ів (по 20 постів = 200 постів)
            for offset in range(0, 200, 20):
                cache.delete(f"popular:{sort}:{cat}::{offset}")
                cache.delete(f"popular:{sort}:{cat}:20:{offset}")

    # Трендові
    for days in [7, 14, 30, 180]:
        for limit in [12, 30]:
            for cat in cats:
                cache.delete(f"trending:{days}:{limit}:{cat}")


# ── Видалення файлів з R2 ─────────────────────────────────────

def _delete_file(field):
    """Безпечно видаляє файл зі сховища якщо він існує"""
    if field and field.name:
        try:
            field.storage.delete(field.name)
        except Exception:
            pass  # Не падаємо якщо файл вже видалений або недоступний


# Post — головне зображення
@receiver(pre_save, sender=Post)
def post_image_on_update(sender, instance, **kwargs):
    """Видаляє старе зображення якщо юзер завантажив нове"""
    if not instance.pk:
        return
    try:
        old = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        _delete_file(old.image)


@receiver(post_delete, sender=Post)
def post_image_on_delete(sender, instance, **kwargs):
    """Видаляє зображення поста при видаленні поста"""
    _delete_file(instance.image)


# PostImages — додаткові зображення
@receiver(pre_save, sender=PostImages)
def post_extra_image_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = PostImages.objects.get(pk=instance.pk)
    except PostImages.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        _delete_file(old.image)


@receiver(post_delete, sender=PostImages)
def post_extra_image_on_delete(sender, instance, **kwargs):
    _delete_file(instance.image)


# PostVideo
@receiver(post_delete, sender=PostVideo)
def post_video_on_delete(sender, instance, **kwargs):
    _delete_file(instance.video)
