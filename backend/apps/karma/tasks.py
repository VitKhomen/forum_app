"""
Асинхронне нарахування карми через Celery.

Чому це окрема таска, а не просто User.add_karma() в сигналі:
- Сигнал викликається синхронно в тому ж HTTP-запиті, що й сам факт
  (наприклад, створення поста). Якщо нарахування карми гальмує
  (БД під навантаженням, лок на рядку юзера) — гальмує і відповідь
  юзеру на "створити пост".
- Виносимо в чергу: пост створюється миттєво, карма нарахується
  через секунду-дві у фоні. Юзер цього не помічає.
"""
import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction, OperationalError

logger = logging.getLogger('apps.karma')

User = get_user_model()


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,        # секунд перед повтором
    ignore_result=True,           # нам не треба знати результат — fire & forget
)
def add_karma_task(self, user_id: int, points: int, reason: str):
    """
    Нараховує карму користувачу у фоновому процесі.

    Args:
        user_id: ID користувача (не сам об'єкт — Celery серіалізує в JSON,
                 а передавати об'єкти моделей напряму — погана практика,
                 дані могли застаріти поки таска чекала в черзі)
        points:  скільки нарахувати (може бути від'ємним)
        reason:  людський опис причини, для KarmaHistory
    """
    try:
        with transaction.atomic():
            # select_for_update — блокуємо рядок щоб уникнути race condition
            # якщо кілька тасок для одного юзера виконуються одночасно
            user = User.objects.select_for_update().get(pk=user_id)
            user.add_karma(points, reason)

        logger.info(
            'Karma updated: user_id=%s points=%+d reason="%s"',
            user_id, points, reason
        )

    except User.DoesNotExist:
        # Юзера видалили поки таска чекала в черзі — це нормально, не ретраїмо
        logger.warning(
            'add_karma_task: user_id=%s no longer exists, skipping', user_id)

    except OperationalError as exc:
        # БД тимчасово недоступна / дедлок — варто спробувати ще раз
        logger.error(
            'add_karma_task: DB error for user_id=%s, retrying: %s', user_id, exc)
        raise self.retry(exc=exc)

    except Exception as exc:
        # Будь-що інше неочікуване — логуємо повну трасу, ретраїмо обережно
        logger.exception(
            'add_karma_task: unexpected error for user_id=%s', user_id)
        raise self.retry(exc=exc)
