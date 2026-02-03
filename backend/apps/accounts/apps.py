from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'


class KarmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.karma'
    verbose_name = 'Карма'

    def ready(self):
        import apps.karma.signals
