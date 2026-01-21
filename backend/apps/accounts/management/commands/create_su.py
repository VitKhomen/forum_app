from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Creates a superuser non-interactively using env vars'

    def handle(self, *args, **options):
        User = get_user_model()
        username = config('SUPERUSER_USERNAME', default='admin')
        email = config('SUPERUSER_EMAIL', default='admin@example.com')
        password = config('SUPERUSER_PASSWORD', default='change-me-123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(
                f'Суперюзер "{username}" вже існує.'))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(self.style.SUCCESS(
            f'Суперюзер "{username}" створено успішно!'))
