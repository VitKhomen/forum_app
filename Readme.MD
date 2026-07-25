# JustForum 🗣️

Повнофункціональний форум-сайт з підтримкою постів, коментарів, системою карми, лайків, модерацією та інтегрованою кінотекою на базі TMDB API.

---

## 🧱 Технологічний стек

### Backend
- **Python 3.12** + **Django 5.2** + **Django REST Framework**
- **PostgreSQL** — основна БД
- **Cloudflare R2 (S3-compatible)** — зберігання медіафайлів
- **JWT-автентифікація** (djangorestframework-simplejwt)
- **Celery 5.4** + **Redis (Upstash)** — асинхронні задачі
- **Gunicorn** — WSGI-сервер
- **Docker** — контейнеризація

### Frontend
- **Vue 3** (Composition API) + **Vite**
- **Pinia** — стейт-менеджмент
- **Vue Router** — клієнтська навігація
- **Tailwind CSS v4** — стилізація
- **Axios** — HTTP-клієнт
- **Swiper** — слайдери
- **vue-toastification** — сповіщення

---

## 🚀 Функціонал

### 👤 Акаунти та профілі
- Реєстрація / вхід / вихід через JWT
- Публічний та приватний профіль
- Аватар, ім'я, біографія
- Зміна пароля

### 📝 Пости
- Створення, редагування, видалення
- Статуси: чернетка / опублікований
- Категорії та теги (django-taggit)
- Головне зображення + галерея (до 20 фото) + відео (до 5 файлів)
- Лічильник переглядів
- Пагінація, пошук, фільтрація
- Автосейв чернетки в localStorage
- Цитування поста в коментарях

### 💬 Коментарі
- Деревовидна структура (відповіді на коментарі)
- Цитування з блок-квотою
- Emoji-пікер
- Лайки на коментарях

### ❤️ Лайки
- Лайки постів та коментарів через Generic FK
- Toggle-логіка (лайк / дизлайк одним запитом)

### 🔖 Закладки
- Збереження постів в особисті закладки
- Окрема сторінка `/profile/bookmarks` зі списком
- Toggle одним запитом

### 📤 Шерінг постів
- Кнопка "Поділитись" з дропдауном (Teleport — не обрізається фоном)
- Копіювання посилання в буфер
- Шерінг в Telegram та Twitter/X
- Native Share API для мобільних
- Динамічні OG/Twitter мета-теги (`useOgMeta`) для гарного превʼю в соцмережах

### ⭐ Система карми
- Асинхронне нарахування через Celery + Redis (Upstash)
- Fallback на синхронне нарахування якщо воркер недоступний
- Рівні карми (кожні 100 очок = +1 рівень)
- Таблиця лідерів
- Детальна історія з пагінацією (модальне вікно)

### 🛡️ Модерація
- Кнопка "Поскаржитись" на постах і коментарях (тільки авторизовані)
- Вибір причини: спам, ненависть, дезінформація, NSFW, інше
- Черга скарг для адміна на окремій сторінці `/admin-panel`
- Адмін може видалити контент або відхилити скаргу
- Видалення закриває всі репорти на цей обʼєкт одразу
- Бейдж з кількістю нових скарг в профілі адміна
- Захист сторінки: видима тільки `is_staff` юзерам

### 🔒 Rate Limiting та захист API
- Кастомний `exception_handler` — повертає зрозумілу JSON-відповідь при перевищенні ліміту (замість стандартного DRF-рядка)
- Окремі throttle-класи в `apps/core/throttling.py` для кожної дії:

| Дія | Ліміт |
|-----|-------|
| Коментарі | 5/хв, 30/год |
| Лайки | 20/хв, 200/день |
| Створення постів | 3/хв, 20/день |
| Вхід (brute-force) | 5/хв з IP |
| Реєстрація | 3/год з IP |
| Закладки | 30/хв |

### 🎬 Кінотека (TMDB)
- Пошук фільмів, серіалів, акторів
- Деталі: трейлер, скріншоти, акторський склад, схожі фільми
- Вотчліст, улюблені, оцінки (1–10)
- Рандомний вибір з параметрами (жанр, рік, рейтинг)
- Відображення колекцій кінотеки у профілі

### 📊 Опитування
- Додавання опитування до поста
- Одиночний та множинний вибір
- Перегляд результатів після голосування
- Скасування голосу

### 📬 Зворотний зв'язок
- Форма feedback зберігається в БД + відправляється на пошту

---

## 📁 Структура проєкту

```
/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # Користувачі, JWT, профілі
│   │   ├── main/          # Пости, категорії, медіа
│   │   ├── comments/      # Коментарі (дерево)
│   │   ├── likes/         # Лайки (Generic FK)
│   │   ├── karma/         # Карма, Celery-таски, лідерборд
│   │   ├── movies/        # TMDB-інтеграція, вотчліст
│   │   ├── bookmarks/     # Закладки постів
│   │   ├── polls/         # Опитування до постів
│   │   ├── moderation/    # Репорти, черга адміна
│   │   ├── feedback/      # Форма зворотного зв'язку
│   │   └── core/          # Throttling-класи, кастомний exception handler
│   ├── config/            # Settings, URLs, WSGI, Celery
│   ├── requirements.txt
│   ├── entrypoint.sh      # Gunicorn + Celery worker в одному процесі
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── views/         # Сторінки (posts, profile, movies, auth, admin-panel...)
    │   ├── components/    # UI-компоненти
    │   │   └── ui/        # ShareButton, ReportButton, BookmarkButton...
    │   ├── stores/        # Pinia stores
    │   ├── services/      # API-клієнт (axios)
    │   ├── composables/   # useTheme, useKarma, useOgMeta, useCommentsSync...
    │   └── router/        # Vue Router
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ Запуск

### Передумови
- Python 3.12+
- Node.js 20+
- PostgreSQL
- Redis (локально або Upstash для прода)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Створіть .env файл (приклад нижче)
python manage.py migrate
python manage.py create_su      # Створення суперюзера з env
python manage.py runserver
```

### Celery worker (локально, окремий термінал)

```bash
cd backend
celery -A config worker -l info --pool=solo   # Windows
celery -A config worker -l info               # Linux/Mac
```

> Без запущеного воркера карма нараховується синхронно через fallback — сайт працює нормально.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (backend)

```bash
docker build -t justforum-backend ./backend
docker run -p 8000:8000 --env-file .env justforum-backend
```

---

## 🔐 Змінні середовища (.env)

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/justforum

# Cloudflare R2 (або будь-який S3)
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
AWS_STORAGE_BUCKET_NAME=...
S3_ENDPOINT_URL=https://....r2.cloudflarestorage.com
R2_PUBLIC_DOMAIN=pub-xxx.r2.dev

# Email
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=app-password

# TMDB
TMDB_API_KEY=your-tmdb-api-key

# Redis / Upstash (для кешу та Celery-брокера)
# Кеш використовує db/0, Celery-черга — db/1 (автоматично)
REDIS_URL=rediss://:<password>@<host>.upstash.io:6379

# Superuser (для create_su)
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=change-me

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://yourapp.vercel.app
FRONTEND_URL=http://localhost:5173
```

---

## 🌐 API Ендпоінти (основні)

| Метод | URL | Опис |
|-------|-----|------|
| POST | `/api/v1/auth/register/` | Реєстрація |
| POST | `/api/v1/auth/login/` | Вхід |
| GET/PATCH | `/api/v1/auth/profile/` | Свій профіль |
| GET | `/api/v1/auth/users/<username>/` | Публічний профіль |
| GET/POST | `/api/v1/posts/` | Список / Створення постів |
| GET | `/api/v1/posts/popular/` | Популярні (hot/views/likes) |
| GET | `/api/v1/posts/trending/` | В тренді |
| GET/POST | `/api/v1/comments/` | Коментарі |
| GET | `/api/v1/comments/post/<id>/` | Коментарі до поста |
| POST | `/api/v1/likes/toggle/` | Лайк / Дизлайк |
| GET | `/api/v1/karma/my_karma/` | Моя карма |
| GET | `/api/v1/karma/leaderboard/` | Таблиця лідерів |
| GET/POST | `/api/v1/bookmarks/` | Список закладок |
| POST | `/api/v1/bookmarks/<id>/toggle/` | Додати/видалити закладку |
| POST | `/api/v1/moderation/report/` | Подати скаргу |
| GET | `/api/v1/moderation/admin/queue/` | Черга скарг (is_staff) |
| POST | `/api/v1/moderation/admin/<id>/resolve/` | Видалити контент (is_staff) |
| POST | `/api/v1/moderation/admin/<id>/reject/` | Відхилити скаргу (is_staff) |
| GET | `/api/v1/movies/search/?q=...` | Пошук (TMDB multi) |
| GET | `/api/v1/movies/<id>/` | Деталі фільму/серіалу |
| POST | `/api/v1/movies/<id>/watchlist/` | Вотчліст |
| POST | `/api/v1/movies/<id>/rate/` | Оцінка |
| POST | `/api/v1/polls/` | Створити опитування |
| POST | `/api/v1/polls/<id>/vote/` | Проголосувати |

---

## 🚀 Деплой

Проєкт задеплоєний на:
- **Backend** — [Render](https://render.com) (через `entrypoint.sh`: migrate → collectstatic → gunicorn + celery worker)
- **Frontend** — [Vercel](https://vercel.com)
- **Медіафайли** — Cloudflare R2
- **Redis / черга задач** — [Upstash](https://upstash.com) (безкоштовний tier)

### Celery на Render
Celery worker запускається в тому самому контейнері що й gunicorn (через `entrypoint.sh`) — окремий Background Worker сервіс не потрібен. При падінні воркера карма автоматично нараховується синхронно через fallback.

---

## 📄 Ліцензія

MIT — використовуйте як завгодно.