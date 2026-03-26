# JustForum 🗣️

Повнофункціональний форум-сайт з підтримкою постів, коментарів, системою карми, лайків та інтегрованою кінотекою на базі TMDB API.

---

## 🧱 Технологічний стек

### Backend
- **Python 3.12** + **Django 5.2** + **Django REST Framework**
- **PostgreSQL** — основна БД
- **Cloudflare R2 (S3-compatible)** — зберігання медіафайлів
- **JWT-автентифікація** (djangorestframework-simplejwt)
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
- Головне зображення + галерея (до 10 фото) + відео (до 5 файлів)
- Лічильник переглядів
- Пагінація, пошук, фільтрація

### 💬 Коментарі
- Деревовидна структура (відповіді на коментарі)
- Цитування з блок-квотою
- Emoji-пікер
- Лайки на коментарях

### ❤️ Лайки
- Лайки постів та коментарів через Generic FK
- Toggle-логіка (лайк / дизлайк одним запитом)

### ⭐ Система карми
- Автоматичне нарахування за пости, коментарі, лайки (через Django signals)
- Рівні карми (кожні 100 очок = +1 рівень)
- Таблиця лідерів
- Детальна історія з пагінацією (модальне вікно)

### 🎬 Кінотека (TMDB)
- Пошук фільмів, серіалів, акторів
- Деталі: трейлер, скріншоти, акторський склад, схожі фільми
- Вотчліст, улюблені, оцінки (1–10)
- Рандомний вибір з параметрами (жанр, рік, рейтинг)
- Відображення колекцій кінотеки у профілі

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
│   │   ├── karma/         # Карма, сигнали, лідерборд
│   │   ├── movies/        # TMDB-інтеграція, вотчліст
│   │   └── feedback/      # Форма зворотного зв'язку
│   ├── config/            # Settings, URLs, WSGI
│   ├── requirements.txt
│   ├── entrypoint.sh
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── views/         # Сторінки (posts, profile, movies, auth...)
    │   ├── components/    # UI-компоненти
    │   ├── stores/        # Pinia stores
    │   ├── services/      # API-клієнт (axios)
    │   ├── composables/   # useTheme, useKarma, useCommentsSync
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
| GET | `/api/v1/movies/search/?q=...` | Пошук (TMDB multi) |
| GET | `/api/v1/movies/<id>/` | Деталі фільму/серіалу |
| POST | `/api/v1/movies/<id>/watchlist/` | Вотчліст |
| POST | `/api/v1/movies/<id>/rate/` | Оцінка |

---

## 🚀 Деплой

Проєкт задеплоєний на:
- **Backend** — [Render](https://render.com) (через `entrypoint.sh`: migrate → collectstatic → gunicorn)
- **Frontend** — [Vercel](https://vercel.com)
- **Медіафайли** — Cloudflare R2

---

## 📄 Ліцензія

MIT — використовуйте як завгодно.