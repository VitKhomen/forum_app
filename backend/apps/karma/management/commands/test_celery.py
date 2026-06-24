"""
Швидка перевірка що Celery + Redis + таска карми працюють.

Запуск:
    python manage.py test_celery <username>

Очікуваний результат:
    - В консолі command: "Таска поставлена в чергу..."
    - У вікні де крутиться `celery -A config worker -l info`
      має зʼявитись лог про виконання add_karma_task
    - karma_points юзера зросте на 5 (через секунду-дві, бо countdown=1)
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from apps.karma.tasks import add_karma_task

User = get_user_model()


class Command(BaseCommand):
    help = 'Тестує проходження таски нарахування карми через Celery'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Користувача "{username}" не знайдено')

        self.stdout.write(f'Поточна карма {username}: {user.karma_points}')
        self.stdout.write('Ставлю таску в чергу...')

        result = add_karma_task.apply_async(
            args=[user.pk, 5, 'Тестове нарахування через test_celery'],
            countdown=1,
        )

        self.stdout.write(self.style.SUCCESS(
            f'✓ Таска поставлена в чергу (task_id={result.id}).\n'
            f'Перевір логи воркера та карму юзера через кілька секунд:\n'
            f'  python manage.py shell -c '
            f'"from apps.accounts.models import User; '
            f'print(User.objects.get(username=\'{username}\').karma_points)"'
        ))
