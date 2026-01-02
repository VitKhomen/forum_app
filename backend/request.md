# 🚀 Complete API Tests для Postman

## 📌 Базова URL
```
http://localhost:8000/api/v1
```

---

## 🔧 Postman Environment Setup

### Environment Variables
Створи environment з назвою **"News Site Local"** та додай змінні:

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "access_token": "",
  "refresh_token": "",
  "test_user_id": "",
  "test_post_slug": "",
  "test_category_slug": "",
  "test_comment_id": ""
}
```

---

## 🔐 Auto-save Token Scripts

### Для Login Request
**POST** `/api/v1/auth/login/`

Додай в **Tests** tab:

```javascript
// Save tokens after successful login
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
    pm.environment.set("test_user_id", jsonData.user.id);
    
    console.log("✅ Tokens saved successfully");
    console.log("User ID:", jsonData.user.id);
    console.log("Username:", jsonData.user.username);
}
```

### Для Register Request
**POST** `/api/v1/auth/register/`

Додай в **Tests** tab:

```javascript
// Save tokens after successful registration
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
    pm.environment.set("test_user_id", jsonData.user.id);
    
    console.log("✅ User registered and tokens saved");
    console.log("User ID:", jsonData.user.id);
}
```

### Для Create Post Request
**POST** `/api/v1/posts/`

Додай в **Tests** tab:

```javascript
// Save post slug for future tests
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.environment.set("test_post_slug", jsonData.slug);
    
    console.log("✅ Post created successfully");
    console.log("Post slug:", jsonData.slug);
}
```

### Для Create Category Request
**POST** `/api/v1/categories/`

Додай в **Tests** tab:

```javascript
// Save category slug
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.environment.set("test_category_slug", jsonData.slug);
    
    console.log("✅ Category created");
    console.log("Category slug:", jsonData.slug);
}
```

### Для Create Comment Request
**POST** `/api/v1/comments/`

Додай в **Tests** tab:

```javascript
// Save comment ID
if (pm.response.code === 201) {
    const jsonData = pm.response.json();
    pm.environment.set("test_comment_id", jsonData.id);
    
    console.log("✅ Comment created");
    console.log("Comment ID:", jsonData.id);
}
```

---

## 📁 1. ACCOUNTS (Authentication)

### 1.1 Register User ✅
**POST** `{{base_url}}/auth/register/`

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

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has access token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.expect(jsonData).to.have.property('refresh');
});

pm.test("User object is valid", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.user).to.have.property('id');
    pm.expect(jsonData.user.email).to.eql('test@example.com');
    pm.expect(jsonData.user.username).to.eql('testuser');
});
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
    "created_at": "2025-12-31T10:00:00Z",
    "updated_at": "2025-12-31T10:00:00Z",
    "posts_count": 0,
    "comments_count": 0
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "User register successfully"
}
```

---

### 1.2 Login User ✅
**POST** `{{base_url}}/auth/login/`

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response contains tokens", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.expect(jsonData).to.have.property('refresh');
});
```

---

### 1.3 Get Profile 👤
**GET** `{{base_url}}/auth/profile/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Profile contains user data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('email');
    pm.expect(jsonData).to.have.property('username');
});
```

---

### 1.4 Update Profile 📝
**PATCH** `{{base_url}}/auth/profile/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "bio": "Software developer from Kyiv"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Profile updated successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.first_name).to.eql('Jane');
    pm.expect(jsonData.last_name).to.eql('Smith');
});
```

---

### 1.5 Upload Avatar 🖼️
**PATCH** `{{base_url}}/auth/profile/`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- Key: `avatar` | Type: File | Value: [select image]

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Avatar URL is present", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.avatar).to.not.be.null;
    pm.expect(jsonData.avatar).to.include('http');
});
```

---

### 1.6 Change Password 🔒
**PUT** `{{base_url}}/auth/change-password/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Password changed successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include('successfully');
});
```

---

### 1.7 Refresh Token 🔄
**POST** `{{base_url}}/auth/token/refresh/`

**Body (JSON):**
```json
{
  "refresh": "{{refresh_token}}"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("New tokens received", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.expect(jsonData).to.have.property('refresh');
    
    // Update tokens
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
});
```

---

### 1.8 Logout 🚪
**POST** `{{base_url}}/auth/logout/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "refresh_token": "{{refresh_token}}"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Logout successful", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include('successful');
});
```

---

## 📁 2. CATEGORIES

### 2.1 List All Categories 📋
**GET** `{{base_url}}/categories/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an('array');
});

pm.test("Categories have required fields", function () {
    var jsonData = pm.response.json();
    if (jsonData.length > 0) {
        pm.expect(jsonData[0]).to.have.property('id');
        pm.expect(jsonData[0]).to.have.property('name');
        pm.expect(jsonData[0]).to.have.property('slug');
        pm.expect(jsonData[0]).to.have.property('posts_count');
    }
});
```

---

### 2.2 Create Category ➕
**POST** `{{base_url}}/categories/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "name": "Mems",
  "description": "All about tech and innovations"
}
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Category created with slug", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('slug');
    pm.expect(jsonData.slug).to.eql('technology');
});

pm.test("Posts count is zero", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.posts_count).to.eql(0);
});
```

---

### 2.3 Get Category Details 🔍
**GET** `{{base_url}}/categories/{{test_category_slug}}/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Category details are complete", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('name');
    pm.expect(jsonData).to.have.property('description');
});
```

---

### 2.4 Update Category ✏️
**PATCH** `{{base_url}}/categories/{{test_category_slug}}/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "description": "Latest tech news and innovations"
}
```

---

### 2.5 Delete Category ❌
**DELETE** `{{base_url}}/categories/{{test_category_slug}}/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Tests:**
```javascript
pm.test("Status code is 204", function () {
    pm.response.to.have.status(204);
});
```

---

## 📁 3. POSTS

### 3.1 List All Posts 📰
**GET** `{{base_url}}/posts/`

**Query Parameters:**
- `?page=1`
- `?search=django`
- `?category__slug=technology`
- `?ordering=-created_at`
- `?status=published`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has pagination", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('count');
    pm.expect(jsonData).to.have.property('results');
});

pm.test("Posts have required fields", function () {
    var jsonData = pm.response.json();
    if (jsonData.results.length > 0) {
        var post = jsonData.results[0];
        pm.expect(post).to.have.property('id');
        pm.expect(post).to.have.property('title');
        pm.expect(post).to.have.property('slug');
        pm.expect(post).to.have.property('excerpt');
    }
});
```

---

### 3.2 Create Post (Draft) 📝
**POST** `{{base_url}}/posts/`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `title`: "My First Django Post"
- `content`: "This is the full content of my post. It needs to be at least 50 characters long to pass validation. Django is awesome!"
- `category`: 1
- `status`: "draft"
- `tags`: "python,django,web"
- `image`: [select file]

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Post created with slug", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('slug');
    pm.expect(jsonData.status).to.eql('draft');
});
```

---

### 3.3 Create Post (Published) 🚀
**POST** `{{base_url}}/posts/`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `title`: "Django REST Framework Tutorial"
- `content`: "Complete guide to building REST APIs with Django REST Framework. This tutorial covers everything from setup to deployment."
- `category`: 1
- `status`: "published"
- `tags`: "django,rest,api"
- `image`: [select file]

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Post is published", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql('published');
});
```

---

### 3.4 Get Post Details 📖
**GET** `{{base_url}}/posts/{{test_post_slug}}/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Post details complete", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('title');
    pm.expect(jsonData).to.have.property('content');
    pm.expect(jsonData).to.have.property('author_info');
    pm.expect(jsonData).to.have.property('category_info');
    pm.expect(jsonData).to.have.property('images');
    pm.expect(jsonData).to.have.property('videos');
});

pm.test("Views count increased", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.views_count).to.be.a('number');
});
```

---

### 3.5 Update Post ✏️
**PATCH** `{{base_url}}/posts/{{test_post_slug}}/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "title": "Updated Django Tutorial",
  "content": "Updated content with more details about Django REST Framework and best practices.",
  "status": "published"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Post updated successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.title).to.include('Updated');
});
```

---

### 3.6 Delete Post 🗑️
**DELETE** `{{base_url}}/posts/{{test_post_slug}}/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Tests:**
```javascript
pm.test("Status code is 204", function () {
    pm.response.to.have.status(204);
});
```

---

### 3.7 Get My Posts 👤
**GET** `{{base_url}}/posts/my/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("All posts belong to current user", function () {
    var jsonData = pm.response.json();
    var userId = pm.environment.get("test_user_id");
    
    jsonData.results.forEach(function(post) {
        pm.expect(post.author).to.eql(userId);
    });
});
```

---

### 3.8 Get Posts by Tag 🏷️
**GET** `{{base_url}}/posts/by_tag/?tag=python`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("All posts have python tag", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.length > 0) {
        jsonData.forEach(function(post) {
            pm.expect(post.tags).to.include('python');
        });
    }
});
```

---

### 3.9 Popular Posts 📊
**GET** `{{base_url}}/posts/popular/?limit=10`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Posts sorted by views", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.length > 1) {
        for (var i = 0; i < jsonData.length - 1; i++) {
            pm.expect(jsonData[i].views_count).to.be.at.least(jsonData[i+1].views_count);
        }
    }
});
```

---

### 3.10 Trending Posts 🔥
**GET** `{{base_url}}/posts/trending/?limit=10&days=7`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Posts are recent", function () {
    var jsonData = pm.response.json();
    var sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    if (jsonData.length > 0) {
        jsonData.forEach(function(post) {
            var postDate = new Date(post.published_at);
            pm.expect(postDate).to.be.above(sevenDaysAgo);
        });
    }
});
```

---

## 📁 4. POST IMAGES

### 4.1 Upload Multiple Images 🖼️
**POST** `{{base_url}}/posts/{{test_post_slug}}/images/`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `image`: [select file 1]
- `image`: [select file 2]
- `image`: [select file 3]

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Multiple images uploaded", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('count');
    pm.expect(jsonData.count).to.be.above(0);
});
```

---

### 4.2 List Post Images 📋
**GET** `{{base_url}}/posts/{{test_post_slug}}/images/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Images have required fields", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.length > 0) {
        pm.expect(jsonData[0]).to.have.property('id');
        pm.expect(jsonData[0]).to.have.property('image');
        pm.expect(jsonData[0]).to.have.property('order');
    }
});
```

---

### 4.3 Delete Image ❌
**DELETE** `{{base_url}}/posts/{{test_post_slug}}/images/1/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Tests:**
```javascript
pm.test("Status code is 204", function () {
    pm.response.to.have.status(204);
});
```

---

### 4.4 Reorder Images 🔄
**PATCH** `{{base_url}}/posts/{{test_post_slug}}/images/reorder/`

**Headers:**
```
Authorization: Bearer {{access_token}}
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

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Order updated successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include('успішно');
});
```

---

### 4.5 Bulk Delete Images 🗑️
**DELETE** `{{base_url}}/posts/{{test_post_slug}}/images/bulk_delete/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "ids": [1, 2, 3]
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Images deleted", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include('Видалено');
});
```

---

## 📁 5. POST VIDEOS

### 5.1 Upload Video 🎥
**POST** `{{base_url}}/posts/{{test_post_slug}}/videos/`

**Headers:**
```
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Body (form-data):**
- `video`: [select video file - max 100MB]

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Video uploaded successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include('успішно');
});
```

---

### 5.2 List Post Videos 📋
**GET** `{{base_url}}/posts/{{test_post_slug}}/videos/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Videos have required fields", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.length > 0) {
        pm.expect(jsonData[0]).to.have.property('id');
        pm.expect(jsonData[0]).to.have.property('video');
        pm.expect(jsonData[0]).to.have.property('order');
    }
});
```

---

### 5.3 Delete Video ❌
**DELETE** `{{base_url}}/posts/{{test_post_slug}}/videos/1/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

---

### 5.4 Reorder Videos 🔄
**PATCH** `{{base_url}}/posts/{{test_post_slug}}/videos/reorder/`

**Headers:**
```
Authorization: Bearer {{access_token}}
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

### 5.5 Bulk Delete Videos 🗑️
**DELETE** `{{base_url}}/posts/{{test_post_slug}}/videos/bulk_delete/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "ids": [1, 2]
}
```

---

## 📁 6. COMMENTS

### 6.1 List All Comments 💬
**GET** `{{base_url}}/comments/`

**Query Parameters:**
- `?page=1`
- `?post=1`
- `?author=1`
- `?search=django`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has pagination", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('count');
    pm.expect(jsonData).to.have.property('results');
});

pm.test("Comments have required fields", function () {
    var jsonData = pm.response.json();
    
    if (jsonData.results.length > 0) {
        var comment = jsonData.results[0];
        pm.expect(comment).to.have.property('id');
        pm.expect(comment).to.have.property('content');
        pm.expect(comment).to.have.property('author_info');
    }
});
```

---

### 6.2 Create Comment ➕
**POST** `{{base_url}}/comments/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "post": 1,
  "content": "Great article! Thanks for sharing this information."
}
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Comment created successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData.content).to.include('Great article');
});
```

---

### 6.3 Create Reply Comment 💬
**POST** `{{base_url}}/comments/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "post": 1,
  "parent": 1,
  "content": "Thank you for your comment! Glad you found it helpful."
}
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Reply created successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.parent).to.not.be.null;
    pm.expect(jsonData.is_reply).to.be.true;
});
```

---

### 6.4 Get Comment Details 🔍
**GET** `{{base_url}}/comments/{{test_comment_id}}/`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Comment has replies array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('replies');
    pm.expect(jsonData.replies).to.be.an('array');
});
```

---

### 6.5 Update Comment ✏️
**PATCH** `{{base_url}}/comments/{{test_comment_id}}/`

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Body (JSON):**
```json
{
  "content": "Updated comment content with more details."
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Comment updated successfully", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.content).to.include('Updated');
});
```

---
