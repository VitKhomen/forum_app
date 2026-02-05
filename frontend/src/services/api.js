import axios from 'axios'
import Cookies from 'js-cookie'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    // 'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Якщо дані це FormData, видаляємо Content-Type 
    // щоб браузер сам встановив правильний з boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = Cookies.get('refresh_token')
      
      if (!refreshToken) {
        return Promise.reject(error)
      }
      
      try {
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/token/refresh/`,
          { refresh: refreshToken }
        )
        
        Cookies.set('access_token', data.access)
        api.defaults.headers.Authorization = `Bearer ${data.access}`
        
        return api(originalRequest)
      } catch (refreshError) {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => {
    // Якщо data це FormData або містить файли, не встановлюємо Content-Type
    return api.patch('/auth/profile/', data)
  },
  changePassword: (data) => api.post('/auth/change-password/', data),
}

// Posts API
export const postsAPI = {
  getAll: (params) => api.get('/posts/', { params }),
  getBySlug: (slug) => api.get(`/posts/${slug}/`),
  create: (data) => api.post('/posts/', data),
  update: (slug, data) => api.patch(`/posts/${slug}/`, data),
  delete: (slug) => api.delete(`/posts/${slug}/`),
  getMy: (params) => api.get('/posts/my/', { params }),
  getByTag: (tag, params) => api.get('/posts/by_tag/', { params: { tag, ...params } }),
  getPopular: (params) => api.get('/posts/popular/', { params }),
  getTrending: (params) => api.get('/posts/trending/', { params }),
  getById: (id) => api.get(`/posts/${id}/`),
  
  // Методи для роботи з додатковими зображеннями
  addImages: (slug, formData) => {
    return api.post(`/posts/${slug}/images/`, formData)
  },
  
  bulkDeleteImages: (slug, imageIds) => {
    return api.delete(`/posts/${slug}/images/bulk_delete/`, {
      data: { ids: imageIds }  // ← передаємо масив у body
    })
  },
  
  // Методи для роботи з відео
  addVideos: (slug, formData) => {
    return api.post(`/posts/${slug}/videos/`, formData)
  },
  
  bulkDeleteVideos: (slug, videoIds) => {
    return api.delete(`/posts/${slug}/videos/bulk_delete/`, {
      data: { ids: videoIds }
    })
  },
}

// Categories API
export const categoriesAPI = {
  getAll: (params) => api.get('/categories/', { params }),
  getBySlug: (slug) => api.get(`/categories/${slug}/`),
}

// Comments API
export const commentsAPI = {
  getAll: (params) => api.get('/comments/', { params }),
  getByPost: (postId, params) => api.get(`/comments/post/${postId}/`, { params }),
  create: (data) => api.post('/comments/', data),
  update: (id, data) => api.patch(`/comments/${id}/`, data),
  delete: (id) => api.delete(`/comments/${id}/`),
  getMy: (params) => api.get('/comments/my-comments/', { params }),
  getReplies: (commentId, params) => api.get(`/comments/post/${commentId}/replies/`, { params }),
}

// Feedback API
export const feedbackAPI = {
  send: (data) => api.post('/feedback/send/', data),
}

// Likes API
export const likesAPI = {
  toggle: (contentType, objectId) => api.post('/likes/toggle/', {
    content_type: contentType,
    object_id: objectId
  }),
  
  getCount: (contentType, objectId) => api.get('/likes/count/', {
    params: { content_type: contentType, object_id: objectId }
  }),
}

export const karmaAPI = {
  getMyKarma: () => api.get('/karma/my_karma/'),
  getMyKarmaHistory: (params) => api.get('/karma/my_karma/', { params }),
  getUserKarma: (username) => api.get(`/karma/user/${username}/`),
  getUserKarmaHistory: (username, params) => api.get(`/karma/user/${username}/`, { params }),
  getLeaderboard: (params) => api.get('/karma/leaderboard/', { params }),
}

export default api