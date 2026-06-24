"""
Ініціалізація Celery для проєкту.
 
Запуск воркера локально:
    celery -A config worker -l info --pool=solo   # Windows
    celery -A config worker -l info                # Linux/Mac
 
В Docker / на проді запускається окремим процесом (другий контейнер /
другий entrypoint), бо worker і web — різні процеси.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('justforum')

# Бере всі CELERY_* налаштування з settings.py (namespace='CELERY' означає
# що в settings.py змінні мають префікс CELERY_, напр. CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично знаходить tasks.py у кожному додатку з INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестове завдання — перевірити що celery взагалі працює"""
    print(f'Request: {self.request!r}')
