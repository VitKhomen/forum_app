from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post


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
