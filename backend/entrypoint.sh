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

echo ""
echo "🚀 Запуск Gunicorn на порту ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output