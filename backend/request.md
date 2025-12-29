# API Tests для Postman

## Базова URL
```
http://localhost:8000/api/v1
```

---

## 📁 ACCOUNTS (Authentication)

### 1. Register User
**POST** `/api/v1/auth/register/`

**Body (JSON):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Expected Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "avatar": null,
    "bio": "",
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z",
    "posts_count": 0,
    "comments_count": 0
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "User register successfully"
}
```

---

### 2. Login User
**POST** `/api/v1/auth/login/`

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

**Expected Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "avatar": null,
    "bio": "",
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z",
    "posts_count": 0,
    "comments_count": 0
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "User login successfully"
}
```

**⚠️ Збережи `access` token для наступних запитів!**

---

### 3. Get Profile
**GET** `/api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "avatar": null,
  "bio": "",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z",
  "posts_count": 0,
  "comments_count": 0
}
```

---

### 4. Update Profile
**PATCH** `/api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "bio": "Software developer from Kyiv"
}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "avatar": null,
  "bio": "Software developer from Kyiv",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:05:00Z",
  "posts_count": 0,
  "comments_count": 0
}
```

---

### 5. Update Avatar
**PATCH** `/api/v1/auth/profile/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (form-data):**
- Key: `avatar` | Type: File | Value: [select image file]

**Expected Response (200):**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "full_name": "Jane Smith",
  "avatar": "https://your-cdn.com/avatars/2025/12/avatar.jpg",
  "bio": "Software developer from Kyiv",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:10:00Z",
  "posts_count": 0,
  "comments_count": 0
}
```

---

### 6. Change Password
**PUT** `/api/v1/auth/change-password/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Expected Response (200):**
```json
{
  "message": "Password change successfully"
}
```

---

### 7. Refresh Token
**POST** `/api/v1/auth/token/refresh/`

**Body (JSON):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Expected Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 8. Logout
**POST** `/api/v1/auth/logout/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Expected Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

## 📁 CATEGORIES

### 9. List Categories
**GET** `/api/v1/categories/`

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "description": "Tech news and articles",
    "posts_count": 5,
    "created_at": "2025-12-28T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Sports",
    "slug": "sports",
    "description": "Sports updates",
    "posts_count": 3,
    "created_at": "2025-12-28T10:00:00Z"
  }
]
```

---

### 10. Create Category
**POST** `/api/v1/categories/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "name": "Technology",
  "description": "All about tech and innovations"
}
```

**Expected Response (201):**
```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "All about tech and innovations",
  "posts_count": 0,
  "created_at": "2025-12-28T10:00:00Z"
}
```

---

### 11. Get Category Details
**GET** `/api/v1/categories/{slug}/`

**Example:**
```
GET /api/v1/categories/technology/
```

**Expected Response (200):**
```json
{
  "id": 1,
  "name": "Technology",
  "slug": "technology",
  "description": "All about tech and innovations",
  "posts_count": 5,
  "created_at": "2025-12-28T10:00:00Z"
}
```

---

### 12. Update Category
**PATCH** `/api/v1/categories/{slug}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "description": "Latest tech news and innovations"
}
```

---

### 13. Delete Category
**DELETE** `/api/v1/categories/{slug}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (204 No Content)**

---

## 📁 POSTS

### 14. List All Posts
**GET** `/api/v1/posts/`

**Query Parameters:**
- `?page=1` - pagination
- `?search=django` - search in title/content/tags
- `?category__slug=technology` - filter by category
- `?ordering=-created_at` - sort by date
- `?status=published` - filter by status

**Example:**
```
GET /api/v1/posts/?category__slug=technology&search=django&page=1
```

**Expected Response (200):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Django",
      "slug": "introduction-to-django",
      "excerpt": "Django is a high-level Python web framework that encourages rapid development...",
      "image": "https://your-cdn.com/posts/2025/12/28/django.jpg",
      "category": 1,
      "category_name": "Technology",
      "author": 1,
      "author_username": "testuser",
      "status": "published",
      "tags": ["python", "django", "web"],
      "created_at": "2025-12-28T10:00:00Z",
      "updated_at": "2025-12-28T10:00:00Z",
      "published_at": "2025-12-28T10:00:00Z",
      "views_count": 150,
      "comments_count": 5,
      "images_count": 3
    }
  ]
}
```

---

### 15. Get Post Details
**GET** `/api/v1/posts/{slug}/`

**Example:**
```
GET /api/v1/posts/introduction-to-django/
```

**Expected Response (200):**
```json
{
  "id": 1,
  "title": "Introduction to Django",
  "slug": "introduction-to-django",
  "content": "Full content of the post...",
  "image": "https://your-cdn.com/posts/2025/12/28/django.jpg",
  "category": 1,
  "category_info": {
    "id": 1,
    "name": "Technology",
    "slug": "technology"
  },
  "author": 1,
  "author_info": {
    "id": 1,
    "username": "testuser",
    "fullname": "Jane Smith",
    "avatar": "https://your-cdn.com/avatars/avatar.jpg"
  },
  "status": "published",
  "tags": ["python", "django", "web"],
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z",
  "published_at": "2025-12-28T10:00:00Z",
  "views_count": 151,
  "comments_count": 5,
  "images": [
    {
      "id": 1,
      "image": "https://your-cdn.com/posts/2025/12/28/extra/img1.jpg",
      "order": 0
    },
    {
      "id": 2,
      "image": "https://your-cdn.com/posts/2025/12/28/extra/img2.jpg",
      "order": 1
    }
  ],
  "videos": [
    {
      "id": 1,
      "video": "https://your-cdn.com/posts/2025/12/28/videos/video1.mp4",
      "order": 0
    }
  ]
}
```

---

### 16. Create Post (Draft)
**POST** `/api/v1/posts/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `title`: "My First Django Post"
- `content`: "This is the full content of my post. It needs to be at least 50 characters long..."
- `category`: 1
- `status`: "draft"
- `tags`: "python,django,web"
- `image`: [select file]

**Expected Response (201):**
```json
{
  "id": 2,
  "title": "My First Django Post",
  "slug": "my-first-django-post",
  "content": "This is the full content of my post...",
  "image": "https://your-cdn.com/posts/2025/12/28/post-image.jpg",
  "category": 1,
  "status": "draft",
  "tags": ["python", "django", "web"]
}
```

---

### 17. Create Post (Published)
**POST** `/api/v1/posts/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `title`: "Django REST Framework Tutorial"
- `content`: "Complete guide to building REST APIs with Django REST Framework..."
- `category`: 1
- `status`: "published"
- `tags`: "django,rest,api"
- `image`: [select file]

**Expected Response (201):**
```json
{
  "id": 3,
  "title": "Django REST Framework Tutorial",
  "slug": "django-rest-framework-tutorial",
  "content": "Complete guide to building REST APIs...",
  "image": "https://your-cdn.com/posts/2025/12/28/drf.jpg",
  "category": 1,
  "status": "published",
  "tags": ["django", "rest", "api"]
}
```

---

### 18. Update Post
**PATCH** `/api/v1/posts/{slug}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "title": "Updated Title",
  "content": "Updated content that is at least 50 characters long...",
  "status": "published"
}
```

---

### 19. Delete Post
**DELETE** `/api/v1/posts/{slug}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (204 No Content)**

---

### 20. Get My Posts
**GET** `/api/v1/posts/my/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (200):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "title": "My First Django Post",
      "slug": "my-first-django-post",
      "excerpt": "This is the full content...",
      "image": "https://your-cdn.com/posts/...",
      "category": 1,
      "category_name": "Technology",
      "author": 1,
      "author_username": "testuser",
      "status": "draft",
      "tags": ["python", "django", "web"],
      "created_at": "2025-12-28T10:00:00Z",
      "updated_at": "2025-12-28T10:00:00Z",
      "published_at": null,
      "views_count": 0,
      "comments_count": 0,
      "images_count": 0
    }
  ]
}
```

---

### 21. Get Posts by Tag
**GET** `/api/v1/posts/by_tag/?tag=python`

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Django",
    "slug": "introduction-to-django",
    "excerpt": "Django is a high-level...",
    "image": "https://your-cdn.com/...",
    "category": 1,
    "category_name": "Technology",
    "author": 1,
    "author_username": "testuser",
    "status": "published",
    "tags": ["python", "django", "web"],
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z",
    "published_at": "2025-12-28T10:00:00Z",
    "views_count": 150,
    "comments_count": 5,
    "images_count": 3
  }
]
```

---

### 22. Popular Posts
**GET** `/api/v1/posts/popular/?limit=10`

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "title": "Introduction to Django",
    "slug": "introduction-to-django",
    "excerpt": "Django is a high-level...",
    "views_count": 1500,
    "...": "..."
  }
]
```

---

### 23. Trending Posts
**GET** `/api/v1/posts/trending/?limit=10&days=7`

**Expected Response (200):**
```json
[
  {
    "id": 3,
    "title": "Django REST Framework Tutorial",
    "slug": "django-rest-framework-tutorial",
    "excerpt": "Complete guide...",
    "views_count": 500,
    "published_at": "2025-12-27T10:00:00Z",
    "...": "..."
  }
]
```

---

## 📁 POST IMAGES

### 24. Upload Multiple Images
**POST** `/api/v1/posts/{post_slug}/images/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `image`: [select file 1]
- `image`: [select file 2]
- `image`: [select file 3]

**Expected Response (201):**
```json
{
  "message": "Файли успішно завантажено",
  "count": 3
}
```

---

### 25. List Post Images
**GET** `/api/v1/posts/{post_slug}/images/`

**Example:**
```
GET /api/v1/posts/my-first-django-post/images/
```

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "image": "https://your-cdn.com/posts/2025/12/28/extra/img1.jpg",
    "order": 0
  },
  {
    "id": 2,
    "image": "https://your-cdn.com/posts/2025/12/28/extra/img2.jpg",
    "order": 1
  }
]
```

---

### 26. Delete Image
**DELETE** `/api/v1/posts/{post_slug}/images/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Example:**
```
DELETE /api/v1/posts/my-first-django-post/images/1/
```

**Expected Response (204 No Content)**

---

### 27. Reorder Images
**PATCH** `/api/v1/posts/{post_slug}/images/reorder/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "orders": {
    "1": 2,
    "2": 0,
    "3": 1
  }
}
```

**Expected Response (200):**
```json
{
  "message": "Порядок успішно оновлено"
}
```

---

### 28. Bulk Delete Images
**DELETE** `/api/v1/posts/{post_slug}/images/bulk_delete/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "ids": [1, 2, 3]
}
```

**Expected Response (200):**
```json
{
  "message": "Видалено 3 елементів"
}
```

---

## 📁 POST VIDEOS

### 29. Upload Video
**POST** `/api/v1/posts/{post_slug}/videos/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `video`: [select video file - max 100MB]

**Expected Response (201):**
```json
{
  "message": "Файли успішно завантажено",
  "count": 1
}
```

---

### 30. List Post Videos
**GET** `/api/v1/posts/{post_slug}/videos/`

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "video": "https://your-cdn.com/posts/2025/12/28/videos/video1.mp4",
    "order": 0
  }
]
```

---

### 31. Delete Video
**DELETE** `/api/v1/posts/{post_slug}/videos/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Expected Response (204 No Content)**

---

### 32. Reorder Videos
**PATCH** `/api/v1/posts/{post_slug}/videos/reorder/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "orders": {
    "1": 0,
    "2": 1
  }
}
```

---

### 33. Bulk Delete Videos
**DELETE** `/api/v1/posts/{post_slug}/videos/bulk_delete/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Body (JSON):**
```json
{
  "ids": [1, 2]
}
```

---

## 🔧 POSTMAN SETUP

### Environment Variables
Створи environment з такими змінними:

```
base_url: http://localhost:8000/api/v1
access_token: (буде автоматично встановлено після login)
refresh_token: (буде автоматично встановлено після login)
```

### Auto-save Token Script
Додай в Tests для Login request:

```javascript
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
}
```

### Authorization Header
Для запитів що потребують авторизації:
```
Authorization: Bearer {{access_token}}
```

---

## ✅ Testing Checklist

### Accounts
- [ ] Register new user
- [ ] Login user (save tokens)
- [ ] Get profile
- [ ] Update profile
- [ ] Upload avatar
- [ ] Change password
- [ ] Refresh token
- [ ] Logout

### Categories
- [ ] List categories
- [ ] Create category
- [ ] Get category details
- [ ] Update category
- [ ] Delete category

### Posts
- [ ] List all posts
- [ ] Get post details
- [ ] Create draft post
- [ ] Create published post
- [ ] Update post
- [ ] Delete post
- [ ] Get my posts
- [ ] Get posts by tag
- [ ] Popular posts
- [ ] Trending posts

### Images
- [ ] Upload multiple images
- [ ] List images
- [ ] Delete single image
- [ ] Reorder images
- [ ] Bulk delete images

### Videos
- [ ] Upload video
- [ ] List videos
- [ ] Delete video
- [ ] Reorder videos
- [ ] Bulk delete videos

---

## ⚠️ Common Errors

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Fix:** Add `Authorization: Bearer {token}` header

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Fix:** You're not the author of the post/object

### 400 Bad Request
```json
{
  "title": ["This field is required."],
  "content": ["Content must be at least 50 characters"]
}
```
**Fix:** Check validation errors and fix request body

### 404 Not Found
```json
{
  "detail": "Not found."
}
```
**Fix:** Check if slug/id exists in database