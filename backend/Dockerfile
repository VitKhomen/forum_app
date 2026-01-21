FROM python:3.12-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіюємо та встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо проект
COPY . .

# ⚠️ ВАЖЛИВО: Даємо права на виконання
RUN chmod +x entrypoint.sh

# Встановлюємо змінні середовища
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["./entrypoint.sh"]