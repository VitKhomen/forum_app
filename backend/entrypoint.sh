#!/usr/bin/env sh
set -e

echo "====================================="
echo "     Запуск Django на Render        "
echo "====================================="

echo "📁 Поточна директорія: $(pwd)"
echo "📄 Структура проекту:"
ls -la

echo "🔍 Перевірка wsgi.py:"
if [ -f "config/wsgi.py" ]; then
    echo "✅ wsgi.py знайдено"
else
    echo "❌ wsgi.py НЕ ЗНАЙДЕНО!"
    exit 1
fi

echo ""
echo "🗄️  Запуск міграцій..."
python manage.py migrate --noinput

echo ""
echo "👤 Створення суперюзера..."
python manage.py create_su || true

echo ""
echo "📦 Збір статичних файлів..."
python manage.py collectstatic --noinput --clear

# ============================================
# CELERY WORKER — запускається у фоні (&) в тому ж
# контейнері, паралельно з gunicorn.
#
# Компроміс: один контейнер на двох процесів.
# Якщо контейнер впаде — падає і сайт, і черга карми.
# Для невеликого навантаження (форум на старті) це ОК,
# бо економить $7/міс окремого Render Background Worker.
#
# Коли проєкт виросте — винеси цей блок в окремий
# entrypoint.worker.sh і підніми окремий Background Worker
# сервіс на Render (дивись deployment_notes.txt).
# ============================================

echo ""
echo "🌿 Запуск Celery worker у фоні..."

# concurrency=2 — досить для невеликого навантаження карми,
# не з'їдає весь RAM контейнера (Render Starter = 512MB)
celery -A config worker \
    --loglevel=info \
    --concurrency=2 \
    --max-tasks-per-child=200 \
    --without-heartbeat \
    --without-gossip \
    --without-mingle \
    > /tmp/celery.log 2>&1 &

CELERY_PID=$!
echo "✅ Celery worker запущено, PID=$CELERY_PID (логи в /tmp/celery.log)"

# Якщо celery воркер впаде одразу при старті (напр. не може
# підключитись до Redis) — побачимо це в перші секунди
sleep 2
if ! kill -0 $CELERY_PID 2>/dev/null; then
    echo "⚠️  УВАГА: Celery worker не запустився! Перевір /tmp/celery.log"
    cat /tmp/celery.log
    # Не валимо весь деплой через це — сайт має жити навіть
    # якщо черга недоступна (карма просто не нарахується)
fi

# ============================================
# Graceful shutdown: коли Render надсилає SIGTERM
# контейнеру, прибиваємо і celery worker, і gunicorn.
#
# ВАЖЛИВО: тут НЕ використовуємо `exec gunicorn`, бо exec
# замінює сам shell-процес на gunicorn — і тоді trap нижче
# просто не спрацює (shell-процесу, що його тримає, вже нема).
# Замість цього запускаємо gunicorn у фоні теж і чекаємо `wait`,
# що дозволяє shell лишитись "живим" і ловити сигнали.
# ============================================

cleanup() {
    echo "🛑 Отримано сигнал зупинки, гашу процеси..."
    kill $CELERY_PID 2>/dev/null || true
    kill $GUNICORN_PID 2>/dev/null || true
    wait
    echo "✅ Всі процеси зупинено"
}
trap cleanup TERM INT

echo ""
echo "🚀 Запуск Gunicorn на порту ${PORT:-8000}..."
gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output &

GUNICORN_PID=$!

# Чекаємо на будь-який з двох процесів — якщо один впаде,
# контейнер має перезапуститись (Render сам це підхопить)
wait -n $GUNICORN_PID $CELERY_PID
EXIT_CODE=$?

echo "⚠️  Один з процесів завершився (код $EXIT_CODE), зупиняю інший..."
cleanup
exit $EXIT_CODE